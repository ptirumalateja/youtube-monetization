const clamp=(x,a,b)=>Math.min(b,Math.max(a,x)); const lerp=(a,b,t)=>a+(b-a)*t;
const SC={};
SC.T=async function(){
  const S=new THREE.Scene(); S.background=new THREE.Color('#d98a62');
  const sky=new THREE.Mesh(new THREE.SphereGeometry(50000,32,16),skyMat('#1f3358','#b8574f','#ff9550',new THREE.Vector3(-0.2,0.05,-1),'#ffd08a',0.0012)); S.add(sky);
  const gr=new THREE.Mesh(new THREE.PlaneGeometry(200000,200000),new THREE.MeshStandardMaterial({color:'#6a5a50',roughness:1})); gr.rotation.x=-Math.PI/2; S.add(gr);
  const sun=new THREE.DirectionalLight('#ffd2a0',3.2); sun.position.set(-300,400,800); S.add(sun); S.add(new THREE.HemisphereLight('#d8a890','#3a2a28',0.9));
  const cam=new THREE.PerspectiveCamera(24,W/H,0.01,200000);
  const objs={mug:mkMug(),bat:mkBat(),person:mkPerson(),hoop:mkHoop(),giraffe:mkGiraffe(),liberty:mkLiberty(),eiffel:mkEiffel(),burj:mkBurj(),everest:mkEverest(),plane:mkAirliner()};
  const sz={mug:0.095,bat:0.86,person:1.72,hoop:3.4,giraffe:5.7,liberty:93,eiffel:330,burj:828,everest:8849,plane:70};
  for(const k in objs){objs[k].visible=false; S.add(objs[k]);}
  const C=compose(S,cam,[0.25,0.5,0.9]);
  return {render(p){ for(const k in objs)objs[k].visible=(k===p.o); const o=objs[p.o]; const h=sz[p.o]; o.position.set(0,0,0); if(p.o==='plane')o.position.y=h*2;
    const d=h*(p.o==='everest'?1.8:p.o==='plane'?2.4:3.0); cam.position.set(d*0.25,h*(p.o==='plane'?2.0:0.45),d); cam.lookAt(0,h*(p.o==='plane'?2:0.5),0); cam.near=d*0.01; cam.far=d*200; cam.updateProjectionMatrix();
    sky.position.copy(cam.position); sky.scale.setScalar(Math.max(1,d*0.01)); C.render(); return {marks:[]}; }};
};
window.__scenes={};
window.renderLayer=async(name,p)=>{ if(!window.__scenes[name])window.__scenes[name]=await SC[name](); const r=window.__scenes[name].render(p); return {img:R.domElement.toDataURL('image/jpeg',0.92),...r}; };
window.ready=true;
