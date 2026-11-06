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
