
// ======================================================= familiar objects at true size (metres, base on y=0)
const M_=(c,r=0.7,m=0.0,e=null,ei=0)=>new THREE.MeshStandardMaterial({color:c,roughness:r,metalness:m,emissive:e||'#000',emissiveIntensity:ei});
function mkMug(){const g=new THREE.Group(); const w=M_('#f2efe8',0.35,0.0,'#6a625a',0.2);
  const b=new THREE.Mesh(new THREE.CylinderGeometry(0.041,0.036,0.095,40,1,true),w); b.position.y=0.0475; g.add(b);
  const bot=new THREE.Mesh(new THREE.CircleGeometry(0.036,40),w); bot.rotation.x=-Math.PI/2; bot.position.y=0.001; g.add(bot);
  const cof=new THREE.Mesh(new THREE.CircleGeometry(0.039,40),M_('#2a160c',0.2)); cof.rotation.x=-Math.PI/2; cof.position.y=0.084; g.add(cof);
  const h=new THREE.Mesh(new THREE.TorusGeometry(0.025,0.006,10,24,Math.PI*1.3),w); h.position.set(0.042,0.05,0); h.rotation.z=-Math.PI*0.65; g.add(h);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(0.0405,0.0016,8,40),w); rim.rotation.x=Math.PI/2; rim.position.y=0.095; g.add(rim); return g;}
function mkBat(){const pts=[[0,0],[0.02,0],[0.024,0.012],[0.011,0.03],[0.0115,0.30],[0.016,0.48],[0.03,0.64],[0.035,0.74],[0.034,0.84],[0.0,0.86]].map(p=>new THREE.Vector2(p[0],p[1]));
  const m=new THREE.Mesh(new THREE.LatheGeometry(pts,36),M_('#c79a62',0.55,0.0,'#3a2412',0.25)); const g=new THREE.Group(); g.add(m); return g;}
function mkPerson(){const g=new THREE.Group(); const pm=M_('#7a6a64',0.85,0,'#3a2b26',0.5); const sk=M_('#a8765a',0.8,0,'#3a2418',0.4);
  const part=(geo,x,y,z,mat=pm,rz=0)=>{const m=new THREE.Mesh(geo,mat); m.position.set(x,y,z); m.rotation.z=rz; g.add(m); return m;};
  part(new THREE.CapsuleGeometry(0.17,0.5,6,12),0,1.17,0,M_('#31507a',0.8,0,'#142038',0.4)); part(new THREE.CapsuleGeometry(0.075,0.68,6,10),-0.09,0.43,0,M_('#2a2d36',0.85)); part(new THREE.CapsuleGeometry(0.075,0.68,6,10),0.09,0.43,0,M_('#2a2d36',0.85));
  part(new THREE.CapsuleGeometry(0.052,0.52,6,8),-0.25,1.12,0,M_('#31507a',0.8,0,'#142038',0.4),0.08); part(new THREE.CapsuleGeometry(0.052,0.52,6,8),0.25,1.12,0,M_('#31507a',0.8,0,'#142038',0.4),-0.08);
  part(new THREE.SphereGeometry(0.105,18,14),0,1.63,0,sk); part(new THREE.SphereGeometry(0.108,18,14,0,Math.PI*2,0,Math.PI*0.5),0,1.645,0,M_('#1d1612',0.9)); return g;}
function mkHoop(){const g=new THREE.Group(); const steel=M_('#3b3f48',0.5,0.6);
  const pole=new THREE.Mesh(new THREE.CylinderGeometry(0.07,0.09,3.05+0.3,16),steel); pole.position.set(0,(3.35)/2,0); g.add(pole);
  const arm=new THREE.Mesh(new THREE.BoxGeometry(0.1,0.1,1.2),steel); arm.position.set(0,3.2,0.6); g.add(arm);
  const bb=new THREE.Mesh(new THREE.BoxGeometry(1.8,1.05,0.05),M_('#f4f6f8',0.2,0.0,'#8a9096',0.3)); bb.position.set(0,3.45,1.2); g.add(bb);
  const sq=new THREE.Mesh(new THREE.BoxGeometry(0.59,0.45,0.055),M_('#e8503a',0.4)); sq.position.set(0,3.25,1.2); sq.scale.set(1,1,0.7); const sqi=new THREE.Mesh(new THREE.BoxGeometry(0.5,0.36,0.06),M_('#f4f6f8',0.2,0.0,'#8a9096',0.3)); sqi.position.copy(sq.position); sqi.position.z+=0.001; g.add(sq,sqi);
  const rim=new THREE.Mesh(new THREE.TorusGeometry(0.23,0.012,10,40),M_('#e8642a',0.4)); rim.rotation.x=Math.PI/2; rim.position.set(0,3.05,1.45); g.add(rim);
  const net=new THREE.Mesh(new THREE.CylinderGeometry(0.23,0.14,0.4,16,1,true),new THREE.MeshBasicMaterial({color:'#f2f2f2',wireframe:true,transparent:true,opacity:0.8})); net.position.set(0,2.85,1.45); g.add(net);
  return g;}
function mkGiraffe(){const g=new THREE.Group();
  const tex=canvasTex(256,256,(c,w,h)=>{c.fillStyle='#e0a94a';c.fillRect(0,0,w,h); for(let i=0;i<70;i++){const x=Math.random()*w,y=Math.random()*h,r=10+Math.random()*14; c.fillStyle='#8a4a1c'; c.beginPath(); c.ellipse(x,y,r,r*0.8,Math.random()*3,0,7); c.fill();}});
  const m=new THREE.MeshStandardMaterial({map:tex,roughness:0.85,emissive:'#3a2410',emissiveIntensity:0.35});
  const body=new THREE.Mesh(new THREE.SphereGeometry(1,24,18),m); body.scale.set(1.25,0.55,0.42); body.position.set(0,2.75,0); g.add(body);
  const neck=new THREE.Mesh(new THREE.CylinderGeometry(0.2,0.36,3.1,16),m); neck.position.set(1.15,4.05,0); neck.rotation.z=-0.28; g.add(neck);
  const head=new THREE.Mesh(new THREE.SphereGeometry(0.3,18,14),m); head.scale.set(1.5,0.85,0.85); head.position.set(1.72,5.4,0); head.rotation.z=-0.25; g.add(head);
  for(const sx of [1.45,-1.35]) for(const sz of [-0.22,0.22]){const l=new THREE.Mesh(new THREE.CylinderGeometry(0.09,0.12,2.6,10),m); l.position.set(sx,1.3,sz); g.add(l);}
  const tail=new THREE.Mesh(new THREE.CylinderGeometry(0.04,0.03,1.4,6),m); tail.position.set(-1.7,2.4,0); tail.rotation.z=0.4; g.add(tail);
  for(const sz of [-0.12,0.12]){const o=new THREE.Mesh(new THREE.CylinderGeometry(0.035,0.045,0.35,8),M_('#5a3a1a')); o.position.set(1.6,5.72,sz); g.add(o);}
  g.scale.setScalar(1.0); return g;} // ~5.7 m to the ossicones

function mkLiberty(){const g=new THREE.Group(); const stone=M_('#c9c0ae',0.85,0,'#4a463c',0.2), patina=M_('#6fb3a0',0.6,0.15,'#1e4a40',0.45);
  // pedestal 47 m (incl. fort base) tapering
  const p1=new THREE.Mesh(new THREE.BoxGeometry(36,12,36),stone); p1.position.y=6; g.add(p1);
  const p2=new THREE.Mesh(new THREE.CylinderGeometry(11.5,15.5,35,4,1),stone); p2.rotation.y=Math.PI/4; p2.position.y=12+17.5; g.add(p2);
  const base=47; const robe=new THREE.Mesh(new THREE.LatheGeometry([[0,0],[8.2,0],[7.4,6],[6.2,16],[5.8,24],[4.6,31],[3.2,34],[0,35]].map(p=>new THREE.Vector2(p[0],p[1])),32),patina); robe.position.y=base; g.add(robe);
  const head=new THREE.Mesh(new THREE.SphereGeometry(3.0,20,16),patina); head.position.set(0,base+37,0); g.add(head);
  for(let i=0;i<7;i++){const a=-Math.PI*0.62+i*Math.PI*0.62/3; const sp=new THREE.Mesh(new THREE.ConeGeometry(0.55,5.2,6),patina); sp.position.set(Math.sin(a)*3.4,base+40.2+Math.cos(a)*1.0,Math.cos(a)*0.2*0); sp.rotation.z=-a*0.9; g.add(sp);}
  const arm=new THREE.Mesh(new THREE.CylinderGeometry(1.3,1.9,19,12),patina); arm.position.set(4.2,base+43.5,0); arm.rotation.z=-0.22; g.add(arm);
  const torch=new THREE.Mesh(new THREE.CylinderGeometry(1.5,1.0,3.2,12),M_('#e8b64a',0.4,0.5,'#8a5a10',0.9)); torch.position.set(8.2,base+53.8,0); g.add(torch);
  const flame=new THREE.Mesh(new THREE.ConeGeometry(1.7,5.2,12),M_('#ffd27a',0.3,0.0,'#ffb040',1.6)); flame.position.set(8.4,base+57.6,0); g.add(flame);
  const tab=new THREE.Mesh(new THREE.BoxGeometry(1.8,7.5,5.2),patina); tab.position.set(-5.4,base+27,1.2); tab.rotation.z=0.18; g.add(tab);
  return g;} // total height 47 + ~46 = ~93 m

function mkEiffel(){const g=new THREE.Group(); const iron=new THREE.MeshStandardMaterial({color:'#6b5848',roughness:0.7,metalness:0.3,emissive:'#3a2a1c',emissiveIntensity:0.55,side:THREE.DoubleSide,alphaTest:0.4,transparent:false});
  const prof=[[0,62],[20,52],[57,36],[115,22],[180,13.5],[276,7],[300,4.5],[330,0.6]]; // y, half-width
  const hw=y=>{for(let i=0;i<prof.length-1;i++){const a=prof[i],b=prof[i+1]; if(y<=b[0]){const t=(y-a[0])/(b[0]-a[0]); return a[1]+(b[1]-a[1])*t;}} return 0.6;};
  const tex=canvasTex(256,1024,(c,w,h)=>{c.clearRect(0,0,w,h); c.strokeStyle='#fff'; c.lineWidth=7; c.fillStyle='#fff';
    // X-braced lattice, horizontal bands every 64px
    for(let y=0;y<h;y+=64){c.beginPath(); c.moveTo(0,y); c.lineTo(w,y); c.stroke(); c.beginPath(); c.moveTo(0,y); c.lineTo(w,y+64); c.moveTo(w,y); c.lineTo(0,y+64); c.stroke();}
    c.lineWidth=14; c.beginPath(); c.moveTo(4,0); c.lineTo(4,h); c.moveTo(w-4,0); c.lineTo(w-4,h); c.stroke();},false);
  const mkFace=(rot)=>{const N=60; const geo=new THREE.BufferGeometry(); const pos=[],uv=[],idx=[]; for(let i=0;i<=N;i++){const y=330*i/N; const w=hw(y); pos.push(-w,y,0,w,y,0); uv.push(0,i/N*3.2,1,i/N*3.2);} for(let i=0;i<N;i++){const a=2*i; idx.push(a,a+1,a+2,a+1,a+3,a+2);}
    geo.setAttribute('position',new THREE.Float32BufferAttribute(pos,3)); geo.setAttribute('uv',new THREE.Float32BufferAttribute(uv,2)); geo.setIndex(idx); geo.computeVertexNormals();
    const m=iron.clone(); m.map=tex; m.alphaMap=tex; m.alphaTest=0.35; const mesh=new THREE.Mesh(geo,m); mesh.rotation.y=rot; return mesh;};
  g.add(mkFace(0)); g.add(mkFace(Math.PI/2)); g.add(mkFace(Math.PI/4)); g.add(mkFace(-Math.PI/4));
  // great arch cut-out suggestion: dark filler under the first platform is skipped; platforms
  const pl=(y,w,hh)=>{const p=new THREE.Mesh(new THREE.BoxGeometry(w,hh,w),M_('#5a4838',0.7,0.2,'#2a1c10',0.4)); p.position.y=y; g.add(p);};
  pl(57,70,5); pl(115,42,3.5); pl(276,19,5); const sp=new THREE.Mesh(new THREE.CylinderGeometry(0.4,2.2,60,8),iron); sp.position.y=300; g.add(sp);
  const dome=new THREE.Mesh(new THREE.CylinderGeometry(5,7,14,12),M_('#5a4838',0.7,0.2,'#2a1c10',0.4)); dome.position.y=284; g.add(dome); return g;}

function mkBurj(){const g=new THREE.Group(); const glass=new THREE.MeshStandardMaterial({color:'#aebfd0',roughness:0.25,metalness:0.55,emissive:'#364a60',emissiveIntensity:0.5,map:canvasTex(128,256,(c,w,h)=>{c.fillStyle='#b8c8d8';c.fillRect(0,0,w,h); c.strokeStyle='rgba(60,80,110,0.55)'; c.lineWidth=2; for(let y=0;y<h;y+=8){c.beginPath();c.moveTo(0,y);c.lineTo(w,y);c.stroke();} for(let x=0;x<w;x+=16){c.beginPath();c.moveTo(x,0);c.lineTo(x,h);c.stroke();}})});
  glass.map.wrapS=glass.map.wrapT=THREE.RepeatWrapping;
  const Y=(s)=>{const sh=new THREE.Shape(); // three-lobed footprint
    for(let i=0;i<3;i++){const a=i*Math.PI*2/3+Math.PI/2; const lx=Math.cos(a)*22*s, ly=Math.sin(a)*22*s; const r=17*s; for(let k=0;k<=12;k++){const t=a-1.0+k*(2.0/12); const x=lx+Math.cos(t)*r, y=ly+Math.sin(t)*r; (i===0&&k===0)?sh.moveTo(x,y):sh.lineTo(x,y);} }
    sh.closePath(); return sh;};
  const tiers=[[0,160,1.0],[160,290,0.86],[290,400,0.72],[400,490,0.58],[490,560,0.44],[560,600,0.3]];
  for(const [y0,y1,s] of tiers){const geo=new THREE.ExtrudeGeometry(Y(s),{depth:y1-y0,bevelEnabled:false}); geo.rotateX(-Math.PI/2); const m=glass.clone(); m.map=glass.map.clone(); m.map.needsUpdate=true; m.map.repeat.set(3,(y1-y0)/40); const mesh=new THREE.Mesh(geo,m); mesh.position.y=y0; g.add(mesh);}
  const spire=new THREE.Mesh(new THREE.CylinderGeometry(0.5,5.5,228,10),M_('#d5dbe2',0.3,0.8,'#505a66',0.5)); spire.position.y=600+114; g.add(spire); return g;} // top = 828 m

function mkEverest(){const geo=new THREE.PlaneGeometry(36000,36000,160,160); geo.rotateX(-Math.PI/2); const p=geo.attributes.position;
  const h2=(x,y)=>{const s=Math.sin(x*12.9898+y*78.233)*43758.5453; return s-Math.floor(s);};
  const vn=(x,y)=>{const ix=Math.floor(x),iy=Math.floor(y),fx=x-ix,fy=y-iy; const u=fx*fx*(3-2*fx),v=fy*fy*(3-2*fy); return h2(ix,iy)*(1-u)*(1-v)+h2(ix+1,iy)*u*(1-v)+h2(ix,iy+1)*(1-u)*v+h2(ix+1,iy+1)*u*v;};
  for(let i=0;i<p.count;i++){const x=p.getX(i),z=p.getZ(i); const r=Math.hypot(x,z*0.8); let hh=Math.max(0,1-r/11500); hh=Math.pow(hh,1.35)*8849;
    const rg=vn(x/900,z/900)*0.5+vn(x/260,z/260)*0.28+vn(x/80,z/80)*0.12; hh*=0.78+rg*0.5; hh+=Math.max(0,1-r/20000)*600*vn(x/2500,z/2500); p.setY(i,Math.min(8849,hh));}
  geo.computeVertexNormals();
  const mat=new THREE.ShaderMaterial({uniforms:{sd:{value:new THREE.Vector3(0.4,0.5,0.8).normalize()}},
    vertexShader:`varying vec3 vn,wp; varying float hy; void main(){hy=position.y; vn=normalize(mat3(modelMatrix)*normal); wp=(modelMatrix*vec4(position,1.)).xyz; gl_Position=projectionMatrix*viewMatrix*vec4(wp,1.);}`,
    fragmentShader:`uniform vec3 sd; varying vec3 vn,wp; varying float hy; void main(){vec3 n=normalize(vn); float l=max(dot(n,sd),0.)*0.75+0.35; vec3 rock=mix(vec3(0.32,0.25,0.22),vec3(0.46,0.36,0.30),smoothstep(0.,4000.,hy)); float sn=smoothstep(4800.,6200.,hy+n.y*900.)*smoothstep(0.35,0.75,n.y+0.2); vec3 c=mix(rock,vec3(0.97,0.95,0.93),clamp(sn,0.,1.)); c*=l; c=mix(c,vec3(0.78,0.45,0.34),0.25*(1.-smoothstep(0.,2500.,hy))); gl_FragColor=vec4(c,1.);}`});
  return new THREE.Mesh(geo,mat);}

function mkAirliner(){const g=new THREE.Group(); const body=M_('#f4f4f6',0.4,0.1,'#8a8e98',0.35);
  const fus=new THREE.Mesh(new THREE.CapsuleGeometry(3.1,64,8,16),body); fus.rotation.z=Math.PI/2; g.add(fus);
  const wing=new THREE.Mesh(new THREE.BoxGeometry(14,0.6,64),body); wing.position.set(-4,-0.6,0); wing.rotation.y=0; g.add(wing);
  const w2=wing.clone(); w2.scale.set(0.75,1,1); g.add(w2);
  const fin=new THREE.Mesh(new THREE.BoxGeometry(9,12,0.6),M_('#2f5fa8',0.5)); fin.position.set(-30,7,0); fin.rotation.z=-0.25; g.add(fin);
  const tp=new THREE.Mesh(new THREE.BoxGeometry(6,0.5,24),body); tp.position.set(-31,1.4,0); g.add(tp);
  for(const z of [-17,17,-27,27]){const e=new THREE.Mesh(new THREE.CylinderGeometry(1.4,1.2,5,12),M_('#c8ccd4',0.4,0.6)); e.rotation.z=Math.PI/2; e.position.set(-1,-2.6,z); g.add(e);} return g;}
