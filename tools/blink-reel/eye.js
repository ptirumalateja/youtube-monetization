// An anatomically shaped human eye for the macro shot. Eyeball radius 1 at the group origin, looking down +z.
// Iris 0.5 (12 mm on a 24 mm globe), pupil 0.16, limbal ring, collarette, crypts, radial fibres; a cornea cap that bulges 0.06 and
// reflects the lamp; skin is one height field with an almond opening (palpebral fissure) whose lid margins sit on the globe, a lid crease,
// brow ridge, nasal side and cheek; instanced upper/lower lashes and brow hairs; a pink caruncle in the inner corner.
// update(open, t) is pure: open 1 = relaxed open eye, 0 = shut.
import * as THREE from 'three';
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)); const sstep=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t)}; const lerp=(a,b,t)=>a+(b-a)*t;
const rng=s=>()=>{ s=(s*1664525+1013904223)>>>0; return s/4294967296; };
function tex(w,h,fn,srgb=true){ const c=document.createElement('canvas'); c.width=w; c.height=h; fn(c.getContext('2d'),w,h); const t=new THREE.CanvasTexture(c); if(srgb) t.colorSpace=THREE.SRGBColorSpace; t.anisotropy=8; return t; }

export function buildEye(renderer){
  const G=new THREE.Group();
  // ---------------- environment for wet reflections: dark room, one warm lamp up-left, a faint cool window right
  const envScene=new THREE.Scene(); envScene.background=new THREE.Color(0x020203);
  const pane=(w,h,col,x,y,z)=>{ const m=new THREE.Mesh(new THREE.PlaneGeometry(w,h),new THREE.MeshBasicMaterial({color:col,side:THREE.DoubleSide})); m.position.set(x,y,z); m.lookAt(0,0,0); envScene.add(m); };
  pane(2.2,1.4,new THREE.Color(9,6.5,3.6),-4,4.5,6); pane(1.2,2.0,new THREE.Color(0.5,0.65,0.9),6,0.5,4); pane(14,0.6,new THREE.Color(0.06,0.05,0.04),0,-6,0);
  const pm=new THREE.PMREMGenerator(renderer); const env=pm.fromScene(envScene,0.02).texture;

  // ---------------- eyeball: sclera + iris painted around the texture's top pole, pole turned to +z
  const TW=2048, TH=2048, row=a=>a/Math.PI*TH;
  const irisR=Math.asin(0.5), pupR=Math.asin(0.16), lim=row(irisR), pr=row(pupR);
  const ballTex=tex(TW,TH,(g,w,h)=>{ const R=rng(11);
    // sclera: warm white, bluish under the limbus, vessels growing denser and redder toward the corners (far from the pole)
    const sg=g.createLinearGradient(0,lim,0,h*0.62); sg.addColorStop(0,'#e9e6e4'); sg.addColorStop(0.35,'#efe7e0'); sg.addColorStop(1,'#e8d2c8'); g.fillStyle=sg; g.fillRect(0,0,w,h);
    for(let i=0;i<260;i++){ let x=R()*w, y=lim+40+Math.pow(R(),0.6)*(h*0.55-lim); const red=clamp((y-lim)/(h*0.5)); g.strokeStyle=`rgba(${150+60*R()},${30+30*R()},${35+20*R()},${0.08+0.35*red*R()})`; g.lineWidth=0.6+2.2*R()*red;
      g.beginPath(); g.moveTo(x,y); let ang=-Math.PI/2+(R()-0.5)*0.9; for(let k=0;k<10;k++){ ang+=(R()-0.5)*0.7; x+=Math.cos(ang)*18; y+=Math.sin(ang)*16; g.lineTo(x,y); if(y<lim+12) break; } g.stroke(); }
    { const og=g.createLinearGradient(0,lim,0,h*0.5); og.addColorStop(0,'rgba(40,30,30,0)'); og.addColorStop(0.5,'rgba(60,40,38,0.25)'); og.addColorStop(1,'rgba(50,30,28,0.6)'); g.fillStyle=og; g.fillRect(0,lim,w,h*0.5-lim); }
    // limbal ring (dark, soft outer edge)
    const lg=g.createLinearGradient(0,lim-46,0,lim+26); lg.addColorStop(0,'rgba(25,16,10,1)'); lg.addColorStop(0.55,'rgba(28,20,14,0.92)'); lg.addColorStop(1,'rgba(40,40,48,0)'); g.fillStyle=lg; g.fillRect(0,lim-46,w,72);
    // iris stroma: hazel-brown, warmer and golden near the pupil, darker toward the limbus
    const ig=g.createLinearGradient(0,pr,0,lim-30); ig.addColorStop(0,'#6b3f16'); ig.addColorStop(0.18,'#b5802e'); ig.addColorStop(0.36,'#8a5a22'); ig.addColorStop(0.7,'#6a4a2a'); ig.addColorStop(1,'#3a2a1c'); g.fillStyle=ig; g.fillRect(0,pr,w,lim-30-pr);
    // radial fibres (each column is one direction around the pupil)
    for(let i=0;i<9000;i++){ const x=R()*w, y0=pr+R()*(lim-pr)*0.2, y1=y0+(lim-pr)*(0.3+0.7*R()); const lt=R()<0.55; g.strokeStyle=lt?`rgba(${220+30*R()},${160+50*R()},${90+40*R()},${0.05+0.16*R()})`:`rgba(${30+20*R()},${16+10*R()},${8},${0.08+0.2*R()})`; g.lineWidth=0.8+2.4*R();
      g.beginPath(); g.moveTo(x,y0); g.bezierCurveTo(x+(R()-0.5)*14,y0+(y1-y0)*0.33,x+(R()-0.5)*14,y0+(y1-y0)*0.66,x+(R()-0.5)*10,y1); g.stroke(); }
    // collarette: a wavy raised ring a third of the way out
    const cy=pr+(lim-pr)*0.33; g.lineWidth=6; g.strokeStyle='rgba(215,165,90,0.3)'; g.beginPath(); for(let x=0;x<=w;x+=6){ const y=cy+10*Math.sin(x*0.045)+6*Math.sin(x*0.13); x?g.lineTo(x,y):g.moveTo(x,y); } g.stroke();
    g.lineWidth=3; g.strokeStyle='rgba(60,32,12,0.5)'; g.beginPath(); for(let x=0;x<=w;x+=6){ const y=cy+14+10*Math.sin(x*0.045)+6*Math.sin(x*0.13); x?g.lineTo(x,y):g.moveTo(x,y); } g.stroke();
    // crypts: dark lens-shaped pits around and beyond the collarette; contraction furrows near the limbus
    for(let i=0;i<120;i++){ const x=R()*w, y=cy+(R()-0.3)*(lim-cy)*0.9, rx=6+R()*16, ry=14+R()*36; const cg=g.createRadialGradient(x,y,0,x,y,ry); cg.addColorStop(0,'rgba(22,12,6,0.75)'); cg.addColorStop(1,'rgba(22,12,6,0)'); g.fillStyle=cg; g.beginPath(); g.ellipse(x,y,rx,ry,0,0,7); g.fill(); }
    for(let k=0;k<3;k++){ const fy=lim-70-k*34; g.strokeStyle='rgba(30,18,10,0.35)'; g.lineWidth=2; g.beginPath(); for(let x=0;x<=w;x+=8){ const y=fy+4*Math.sin(x*0.02+k); x?g.lineTo(x,y):g.moveTo(x,y); } g.stroke(); }
    // gold flecks near the pupil
    for(let i=0;i<500;i++){ const x=R()*w, y=pr+10+R()*(cy-pr); g.fillStyle=`rgba(255,${190+50*R()},${100+60*R()},${0.15+0.3*R()})`; g.fillRect(x,y,2+3*R(),3+8*R()); }
    // pupil with the dark pigment ruff at its edge
    g.fillStyle='#030303'; g.fillRect(0,0,w,pr); const pg=g.createLinearGradient(0,pr-2,0,pr+18); pg.addColorStop(0,'rgba(20,10,4,1)'); pg.addColorStop(1,'rgba(20,10,4,0)'); g.fillStyle=pg; g.fillRect(0,pr-2,w,20);
  });
  const ballBump=tex(1024,1024,(g,w,h)=>{ const R=rng(5); g.fillStyle='#808080'; g.fillRect(0,0,w,h); const l=lim/2, p=pr/2; for(let i=0;i<5000;i++){ const x=R()*w, y=p+R()*(l-p); g.fillStyle=`rgba(${R()<0.5?255:0},${R()<0.5?255:0},${R()<0.5?255:0},0.12)`; g.fillRect(x,y,1.5,6+12*R()); } },false);
  const ballM=new THREE.MeshPhysicalMaterial({map:ballTex,bumpMap:ballBump,bumpScale:0.6,roughness:0.42,clearcoat:0.35,clearcoatRoughness:0.08,envMap:env,envMapIntensity:0.12});
  const ball=new THREE.Mesh(new THREE.SphereGeometry(1,192,128),ballM); ball.rotation.x=Math.PI/2;
  const rig=new THREE.Group(); rig.add(ball); G.add(rig);
  // cornea: a clear cap of a smaller sphere (radius 0.78), apex 0.06 proud of the globe, mostly reflection
  const corneaG=new THREE.SphereGeometry(0.78,256,128,0,Math.PI*2,0,0.74); corneaG.rotateX(Math.PI/2);
  const cornea=new THREE.Mesh(corneaG,new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:0.0,metalness:0,transparent:true,opacity:0.03,clearcoat:1,clearcoatRoughness:0,envMap:env,envMapIntensity:2.2,depthWrite:false}));
  cornea.position.z=0.28; rig.add(cornea);

  // ---------------- skin: one height field with the almond opening
  const A=0.88;                         // half-width of the fissure (corners sit on the globe's edge)
  const tilt=x=>0.05*x;                 // lateral corner (x>0) a little higher than the medial one
  const upOpen=x=>{ const u=clamp(1-Math.pow(x/A,2)); return tilt(x)+0.45*Math.pow(u,0.62)*(1-0.12*x); };
  const loOpen=x=>{ const u=clamp(1-Math.pow(x/A,2)); return tilt(x)-0.4*Math.pow(u,0.78)*(1+0.1*x); };
  const shutLine=x=>{ const u=clamp(1-Math.pow(x/A,2)); return tilt(x)-0.22*Math.pow(u,0.8); };
  const NX=340, NY=440, X0=-2.3, X1=2.3, Y0=-3.0, Y1=3.0;
  const skinG=new THREE.PlaneGeometry(X1-X0,Y1-Y0,NX,NY); const pos=skinG.attributes.position;
  const R0=rng(17); const jitter=new Float32Array(pos.count); for(let i=0;i<pos.count;i++) jitter[i]=R0();
  const faceZ=(x,y)=>{ const brow=0.34*Math.exp(-Math.pow((y-1.45)/0.48,2))*(1-0.22*x), cheek=0.2*Math.exp(-Math.pow((y+1.55)/0.62,2)), nose=0.55*sstep(-1.15,-2.3,x)*Math.exp(-Math.pow((y+0.2)/1.6,2)),
    temple=-0.4*sstep(1.05,2.3,x), socket=-0.05*Math.exp(-(x*x/1.3+y*y/0.9)); return 1.1+brow+cheek+nose+temple+socket; };
  const skinTex=tex(1024,1024,(g,w,h)=>{ g.fillStyle='#a8826e'; g.fillRect(0,0,w,h); const R=rng(3); for(let i=0;i<9000;i++){ g.fillStyle=`rgba(${R()<0.5?'120,60,50':'230,190,170'},${0.04+0.06*R()})`; g.beginPath(); g.arc(R()*w,R()*h,0.6+2.2*R(),0,7); g.fill(); } });
  const skinBump=tex(1024,1024,(g,w,h)=>{ g.fillStyle='#808080'; g.fillRect(0,0,w,h); const R=rng(4); for(let i=0;i<40000;i++){ g.fillStyle=R()<0.5?'rgba(60,60,60,0.3)':'rgba(190,190,190,0.2)'; g.beginPath(); g.arc(R()*w,R()*h,0.4+0.9*R(),0,7); g.fill(); } g.strokeStyle='rgba(60,60,60,0.3)'; for(let i=0;i<300;i++){ const y=R()*h; g.lineWidth=0.6; g.beginPath(); g.moveTo(R()*w,y); g.lineTo(R()*w,y+(R()-0.5)*20); g.stroke(); } },false);
  skinTex.wrapS=skinTex.wrapT=skinBump.wrapS=skinBump.wrapT=THREE.RepeatWrapping; skinTex.repeat.set(2,2); skinBump.repeat.set(7,7);
  const skinM=new THREE.MeshPhysicalMaterial({color:0xa88a7a,vertexColors:true,map:skinTex,bumpMap:skinBump,bumpScale:0.22,roughness:0.6,clearcoat:0.07,clearcoatRoughness:0.35,sheen:0.2,sheenRoughness:0.6,sheenColor:new THREE.Color(0xd08070),envMap:env,envMapIntensity:0.15});
  const col=new Float32Array(pos.count*3).fill(1); skinG.setAttribute('color',new THREE.BufferAttribute(col,3)); const skin=new THREE.Mesh(skinG,skinM); G.add(skin);
  let lastKey=-1; const margins={up:[],lo:[]};
  function shapeSkin(open){ const key=Math.round(open*400); if(key===lastKey) return; lastKey=key;
    const s=1-open; const crease=open;
    // the two lid margins as polylines; every vertex gets a true distance to each, so the lids have no seams or stair-steps
    const NS=72, U=[], L=[]; for(let k=0;k<=NS;k++){ const x=-A+2*A*k/NS; const yl=lerp(loOpen(x),shutLine(x),0.3*s); U.push([x,lerp(upOpen(x),yl+0.003,s)]); L.push([x,yl]); }
    const dist=(P,x,y)=>{ let m=1e9; for(let k=0;k<NS;k++){ const ax=P[k][0], ay=P[k][1], bx=P[k+1][0]-ax, by=P[k+1][1]-ay; const t=clamp(((x-ax)*bx+(y-ay)*by)/(bx*bx+by*by)); const dx=x-ax-t*bx, dy=y-ay-t*by, q=dx*dx+dy*dy; if(q<m) m=q; } return Math.sqrt(m); };
    const along=x=>1-sstep(A*0.55,A*1.05,Math.abs(x));
    for(let i=0;i<pos.count;i++){ const ix=i%(NX+1), iy=Math.floor(i/(NX+1)); const x=X0+(X1-X0)*ix/NX, y=Y1-(Y1-Y0)*iy/NY;
      const du=dist(U,x,y), dl=dist(L,x,y); const yl=lerp(loOpen(x),shutLine(x),0.3*s), yu=lerp(upOpen(x),yl+0.003,s);
      const inside=Math.abs(x)<A&&y<yu&&y>yl; const d=Math.min(du,dl), wu=sstep(-0.04,0.04,dl-du);   // wu: 1 on the upper lid, 0 on the lower
      const bulge=0.06*Math.exp(-(x*x+y*y)/0.3);                     // the lid drapes over the cornea, so a shut lid hides it
      const r2=x*x+y*y; let z;
      if(inside){ z=Math.sqrt(Math.max(0,(1.004+bulge)**2-r2))-1.5*d; col[i*3]=0.9; col[i*3+1]=0.55; col[i*3+2]=0.52; }   // margin keeps rolling in behind the globe
      else {
        const Rl=1.004+bulge+0.05*sstep(0,0.07,d);                     // the lid margin rolls onto the globe
        const fz=faceZ(x,y); const zs=Math.sqrt(Math.max(0,Rl*Rl-r2)), lo=fz-0.3, k=0.12, hh=clamp(0.5+0.5*(zs-lo)/k); const zl=lerp(lo,zs,hh)+k*hh*(1-hh);   // smooth max: never a trench
        z=lerp(zl,fz,sstep(0.02,0.65,d)); const al=along(x);
        z-=0.06*crease*Math.exp(-Math.pow((d-0.34)/0.09,2))*al*wu;                                       // upper lid crease (fades before the corners)
        z-=0.008*Math.exp(-Math.pow((d-0.32)/0.12,2))*al*(1-wu);                                         // soft lower lid fold
        z+=0.0015*(jitter[i]-0.5)*sstep(0.1,0.5,d);
        // colour: dark lash line on the upper margin, pink wet margin, darker crease and canthi
        const ll=wu*(1-sstep(0.0,0.035,d)), m=1-sstep(0.0,0.09,d), cr=wu*Math.exp(-Math.pow((d-0.34)/0.1,2))*al, cn=sstep(A-0.15,A+0.15,Math.abs(x))*(1-sstep(0,0.3,d)), dk=1-0.8*ll;
        col[i*3]=(1+0.12*m-0.22*cr-0.35*cn)*dk; col[i*3+1]=(1-0.28*m-0.3*cr-0.45*cn)*dk; col[i*3+2]=(1-0.22*m-0.3*cr-0.45*cn)*dk; }
      pos.setXYZ(i,x,y,z); }
    pos.needsUpdate=true; skinG.attributes.color.needsUpdate=true; skinG.computeVertexNormals();
    // margins for the lashes and the tear line (sampled across the fissure)
    margins.up.length=0; margins.lo.length=0; for(let k=0;k<=120;k++){ const x=-A*0.98+2*A*0.98*k/120; const yl=lerp(loOpen(x),shutLine(x),0.3*s), yu=lerp(upOpen(x),yl+0.003,s); margins.up.push([x,yu]); margins.lo.push([x,yl]); } }

  // ---------------- lashes (instanced curved hairs), brow hairs, caruncle
  const hairM=new THREE.MeshStandardMaterial({color:0x140c08,roughness:0.45});
  function hairGeo(len,curl,r0){ const c=new THREE.QuadraticBezierCurve3(new THREE.Vector3(0,0,0),new THREE.Vector3(0,len*0.55,curl*0.2),new THREE.Vector3(0,len,curl)); const g=new THREE.TubeGeometry(c,8,r0,5,false);
    const p=g.attributes.position; for(let i=0;i<p.count;i++){ const y=p.getY(i)/len; const k=1-0.85*clamp(y); p.setX(i,p.getX(i)*k); p.setZ(i,(p.getZ(i)-curl*y*y)*k+curl*y*y); } return g; }
  const NU=220, NL=60, NB=1300;
  const upL=new THREE.InstancedMesh(hairGeo(1,0.32,0.014),hairM,NU), loL=new THREE.InstancedMesh(hairGeo(1,-0.25,0.008),hairM,NL), brow=new THREE.InstancedMesh(hairGeo(1,0.06,0.009),new THREE.MeshStandardMaterial({color:0x1e130c,roughness:0.6}),NB);
  for(const m of [upL,loL,brow]){ m.frustumCulled=false; G.add(m); }
  const LR=rng(29); const upS=[...Array(NU)].map((_,k)=>({u:clamp(Math.floor(k/3)/(NU/3)+0.012*LR()),l:0.17+0.1*LR(),sp:(LR()-0.5)*0.35,c:LR()})), loS=[...Array(NL)].map(()=>({u:0.15+0.83*LR(),l:0.06+0.05*LR(),sp:(LR()-0.5)*0.4})), brS=[...Array(NB)].map(()=>({u:LR(),v:LR(),l:0.09+0.08*LR(),a:(LR()-0.5)*0.5}));
  const M4=new THREE.Matrix4(), Q=new THREE.Quaternion(), S=new THREE.Vector3(), P=new THREE.Vector3();
  function orient(origin,dirY,dirZ,len,i,mesh){ const y=dirY.clone().normalize(); const z=dirZ.clone().addScaledVector(y,-dirZ.dot(y)).normalize(); const x=new THREE.Vector3().crossVectors(y,z); M4.makeBasis(x,y,z); Q.setFromRotationMatrix(M4); S.set(len,len,len); M4.compose(origin,Q,S); mesh.setMatrixAt(i,M4); }
  function placeHairs(open){ const pick=(arr,u)=>{ const f=u*(arr.length-1), i=Math.floor(f), t=f-i; const a=arr[i], b=arr[Math.min(arr.length-1,i+1)]; return [lerp(a[0],b[0],t),lerp(a[1],b[1],t)]; };
    upS.forEach((h,i)=>{ const [x,y]=pick(margins.up,h.u); const zr=Math.sqrt(Math.max(0,1.07*1.07-x*x-y*y)); P.set(x,y+0.012,zr); const n=P.clone().normalize();
      const lenK=0.55+0.45*Math.sin(Math.PI*clamp(h.u*1.05)); const dir=n.clone().multiplyScalar(1.8).add(new THREE.Vector3(0.45*x+h.sp*0.25,0.3*open-0.55*(1-open),0)); orient(P,dir,new THREE.Vector3(0,1,0.2),h.l*lenK,i,upL); });
    loS.forEach((h,i)=>{ const [x,y]=pick(margins.lo,h.u); const zr=Math.sqrt(Math.max(0,1.09*1.09-x*x-y*y)); P.set(x,y-0.016,zr); const n=P.clone().normalize();
      const dir=n.clone().multiplyScalar(2.2).add(new THREE.Vector3(0.3*x+h.sp*0.3,-0.6,0)); orient(P,dir,new THREE.Vector3(0,-1,0.2),h.l*(0.5+0.5*Math.sin(Math.PI*h.u)),i,loL); });
    brS.forEach((h,i)=>{ const x=lerp(-1.25,1.35,h.u), yb=1.42+0.22*Math.sin(Math.PI*clamp((x+1.25)/2.6))-0.1*h.u+0.24*(h.v-0.5)*(1-0.8*Math.abs(h.u-0.45)); P.set(x,yb,faceZ(x,yb)+0.002);
      const dir=new THREE.Vector3(lerp(0.2,1.0,h.u)+h.a,lerp(0.7,-0.2,h.u),0.06); orient(P,dir,new THREE.Vector3(0,0,1),h.l*(1-0.5*Math.abs(h.u-0.35)),i,brow); });
    upL.instanceMatrix.needsUpdate=loL.instanceMatrix.needsUpdate=brow.instanceMatrix.needsUpdate=true; }
  const caruncle=new THREE.Mesh(new THREE.SphereGeometry(1,24,16),new THREE.MeshPhysicalMaterial({color:0xd07a78,roughness:0.3,clearcoat:1,clearcoatRoughness:0.1,envMap:env,envMapIntensity:0.6})); caruncle.scale.set(0.07,0.075,0.05); caruncle.position.set(-0.8,-0.02,0.5); G.add(caruncle);
  // tear meniscus: a thin wet bead along the lower margin
  const tearM=new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:0,transparent:true,opacity:0.35,clearcoat:1,envMap:env,envMapIntensity:1.5}); let tear=null;
  function placeTear(){ if(tear){ G.remove(tear); tear.geometry.dispose(); } const pts=margins.lo.filter((_,k)=>k%4===0).map(([x,y])=>{ const z=Math.sqrt(Math.max(0,1.012*1.012-x*x-y*y)); return new THREE.Vector3(x,y+0.012,z); }); tear=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(pts),80,0.012,6,false),tearM); G.add(tear); }

  const shM=new THREE.MeshBasicMaterial({color:0x000000,transparent:true,vertexColors:true,depthWrite:false,polygonOffset:true,polygonOffsetFactor:-2});
  shM.onBeforeCompile=sh=>{ sh.fragmentShader=sh.fragmentShader.replace('#include <color_fragment>','diffuseColor.a*=vColor.r;'); };
  const NSH=96, shG=new THREE.BufferGeometry(), shP=new Float32Array((NSH+1)*2*3), shC=new Float32Array((NSH+1)*2*3), shI=[];
  for(let k=0;k<NSH;k++){ const a=2*k; shI.push(a,a+1,a+2,a+1,a+3,a+2); } shG.setIndex(shI); shG.setAttribute('position',new THREE.BufferAttribute(shP,3)); shG.setAttribute('color',new THREE.BufferAttribute(shC,3));
  const shade=new THREE.Mesh(shG,shM); shade.frustumCulled=false; shade.renderOrder=2; G.add(shade);
  function placeShade(open){ for(let k=0;k<=NSH;k++){ const u=k/NSH, f=u*(margins.up.length-1), j=Math.floor(f), t=f-j; const a=margins.up[j], b=margins.up[Math.min(margins.up.length-1,j+1)]; const x=lerp(a[0],b[0],t), y=lerp(a[1],b[1],t);
      const edge=Math.sin(Math.PI*u)**0.4; for(let e=0;e<2;e++){ const yy=y-(e?0.26*edge:0.0), zz=Math.sqrt(Math.max(0,1.0035*1.0035-x*x-yy*yy)); shP.set([x,yy,zz],(2*k+e)*3); const al=e?0:0.85*open*edge; shC.set([al,al,al],(2*k+e)*3); } }
    shG.attributes.position.needsUpdate=shG.attributes.color.needsUpdate=true; }
  return { group:G, rig, cornea, skinM,
    update(open,t){ shapeSkin(open); placeHairs(open); placeTear(); placeShade(open); caruncle.visible=open>0.15;
      rig.rotation.y=0.035*Math.sin(t*1.9)+0.02*Math.sin(t*5.3); rig.rotation.x=0.025*Math.sin(t*1.4); } };
}
