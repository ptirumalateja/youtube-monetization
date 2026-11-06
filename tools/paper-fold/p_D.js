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
    const k=clamp(p.k,0,10); const j=Math.min(9,Math.floor(k)); const pr=k>=10?1:k-j; const e=ease(clamp((pr-0.04)/0.9,0,1));
    let sx=A,sz=B; for(let i=0;i<j;i++){ if(i%2==0)sx/=2; else sz/=2; }
    const T=1e-4*Math.pow(2,j), eps=0.00004;
    if(j%2==0){ // fold the x extent
      stat.scale.set(sx/2,T,sz); stat.position.set(sx/4,T/2+eps,sz/2);
      piv.position.set(sx/2,T+eps,sz/2); piv.rotation.set(0,0,Math.PI*e); mov.scale.set(sx/2,T,sz); mov.position.set(sx/4,-T/2,0);
    } else {
      stat.scale.set(sx,T,sz/2); stat.position.set(sx/2,T/2+eps,sz/4);
      piv.position.set(sx/2,T+eps,sz/2); piv.rotation.set(-Math.PI*e,0,0); mov.scale.set(sx,T,sz/2); mov.position.set(0,-T/2,sz/4);
    }
    const nx=(j%2==0)?lerp(sx,sx/2,e):sx, nz=(j%2==1)?lerp(sz,sz/2,e):sz; const thick=T*(1+e); const ext=Math.max(nx,nz,thick);
    const cx=nx/2, cz=nz/2; const dist=lerp(1.8,0.55,clamp(k/10,0,1))+ext*1.2;
    const yaw=0.25+0.12*Math.sin(k*0.4); const el=0.36;
    cam.position.set(cx+Math.sin(yaw)*dist*0.9, thick+dist*el, cz+Math.cos(yaw)*dist*0.9);
    cam.lookAt(cx-ext*0.04, thick*0.6+ext*0.04, cz);
    cam.fov=26; cam.updateProjectionMatrix(); S.fog.near=dist*0.9; S.fog.far=dist*0.9+1.1;
    const sa=0; nb.visible=false;     nb.position.set(0.012+(1-ease(sa))*0.35,0,-0.17); nb.rotation.y=-0.12;
    bokeh.forEach((b,i)=>{b.material.opacity=0.12+0.2*(0.5+0.5*Math.sin(p.t*0.8+i))});
    C.render(); return {marks:[]};
  }};
};

