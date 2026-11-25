// What Are You Carrying (Slow Light Dark). A cream figure bent double under a huge sack of stones climbs a steep dark hill
// toward the series gold lamp at the top. He slips back, kneels, and throws the stones down the slope one by one (each
// one labelled by the overlay: FEAR, EXCUSES, SELF-DOUBT, TOXIC PEOPLE, BAD HABITS); with every stone he straightens a
// little. Then he stands, walks up light, and steps into the lamp's pool at the top.
//
// Side view: the hill rises along +x (camera on +z). renderAt(t) is pure (no state between frames).
import * as THREE from 'three';
import * as SLD from './sld.js';
const {V,clamp,sstep,lerp,sm5,PAL,rng,rotY}=SLD;
const TL=await (await fetch('./timeline.json')).json();
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960, DUR=TL.duration;

// ---------------------------------------------------------------- the hill: flat ground, a steep smooth rise, a plateau
const HL=5.6, HH=4.4;                                                  // rise length / height (max slope about 50 degrees): steep, and the whole climb fits the tall frame
const hAt=x=>x<=0?0:x>=HL?HH:HH*(()=>{ const u=x/HL; return u*u*(3-2*u); })();
const slopeAt=x=>x<=0||x>=HL?0:HH/HL*6*(x/HL)*(1-x/HL);
const PLAT=V(7.4,HH,0);                                               // where he ends, in the light
// the lamp hangs over the plateau: the new life is the light at the top
// the lamp hangs high over the top and leans down the slope: the upper climb is in its light, the bottom is not
const S=SLD.createStage({W,H,lamp:V(PLAT.x-0.6,HH+7.6,1.4),lampTarget:V(PLAT.x-2.6,HH-0.9,0),cone:0.46,spot:150,beam:0.1,motes:4000,moteSpan:14,moteCx:3});
const {scene,cam}=S; const BEAM=S.NOREFL[0];
cam.near=0.5; cam.far=90; cam.updateProjectionMatrix();
S.spot.shadow.camera.far=16; S.spot.shadow.camera.updateProjectionMatrix();
S.scene.fog.density=0.045;
const R=SLD.createRig(scene);
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.2,rimCol:0xffd9a0,lift:0.035});   // low self-glow, so his lit side and shadow side read as a falloff
// one light rule for the whole film: a warm key from the lamp side (upper right) that follows him. Lit right side, dark left side,
// a long shadow to the left. At the top the same light turns up for the payoff.
const KEY=new THREE.SpotLight(0xffc77a,0,9,0.42,0.6,1.0); KEY.castShadow=true; KEY.shadow.mapSize.set(1024,1024); KEY.shadow.bias=-0.0006;
KEY.shadow.camera.near=1; KEY.shadow.camera.far=10; scene.add(KEY); scene.add(KEY.target);
function keyAt(t,J){ const c=J.neck.clone().lerp(J.hip,0.5); KEY.target.position.copy(c); KEY.position.copy(c).add(V(2.8,2.0,3.6));
  const e=sm5(sstep(TL.glow0,TL.glow1,t)); KEY.intensity=14*(1+1.2*e); }
const P0=R.P0;
// he is drawn 18% bigger than the series rig, so he reads on a phone in the wide shots: joints scaled about his feet (hand targets
// mapped in and back out so held things stay in his hands), limbs thickened to match after posing
const HS=1.18; { const skel0=R.skel; const pin=(t,root)=>t&&t.clone().sub(root).multiplyScalar(1/HS).add(root);
  R.skel=(P,root,yaw)=>{ const Q=(P.tL||P.tR)?{...P,tL:pin(P.tL,root),tR:pin(P.tR,root)}:P; const J=skel0(Q,root,yaw);
    for(const k in J) if(J[k]&&J[k].isVector3) J[k]=J[k].clone().sub(root).multiplyScalar(HS).add(root); return J; };
  const pose0=R.poseFig; R.poseFig=(F,J)=>{ pose0(F,J); F.bones.forEach(b=>{ b.scale.x*=HS; b.scale.z*=HS; }); F.joints.forEach(b=>b.scale.multiplyScalar(HS)); F.head.scale.multiplyScalar(HS); }; }

{ // hill mesh: extruded side profile, 3 m deep, dark stone; a faint cream edge on the near top edge so the line reads in the dark
  const pts=[V(-16,-0.02,0),V(-16,0,0)]; for(let i=0;i<=80;i++){ const x=i/80*HL; pts.push(V(x,hAt(x),0)); } pts.push(V(18,HH,0),V(18,-0.02,0));
  const sh=new THREE.Shape(pts.map(p=>new THREE.Vector2(p.x,p.y)));
  const g=new THREE.ExtrudeGeometry(sh,{depth:3,bevelEnabled:false,curveSegments:1}); g.translate(0,0,-1.5);
  const m=new THREE.Mesh(g,SLD.rimify(new THREE.MeshStandardMaterial({color:0x2f2c28,roughness:0.93,map:SLD.noiseTex(512,9,128,60,120,0.15)}),0x9fb2d6,0.05,'hill'));
  m.receiveShadow=true; m.castShadow=true; scene.add(m);
  const ep=[]; for(let i=0;i<=120;i++){ const x=-6+i/120*(24); ep.push(V(x,hAt(x)+0.006,1.5)); }
  const edge=new THREE.Mesh(new THREE.TubeGeometry(new THREE.CatmullRomCurve3(ep),400,0.012,6,false),new THREE.MeshBasicMaterial({color:new THREE.Color(0xede6d6).multiplyScalar(0.28)}));
  scene.add(edge); }


// ---------------------------------------------------------------- grass: small tufts along the hill's surface, thickest on the near edge so the line gets a soft, living silhouette
const GRASS=(()=>{ const Rn=rng(77); const blade=new THREE.ConeGeometry(0.017,1,3,1); blade.translate(0,0.5,0);
  const mat=SLD.rimify(new THREE.MeshStandardMaterial({color:0x837d66,emissive:0xc9c2a8,emissiveIntensity:0.05,roughness:0.9}),0xfff1d8,0.3,'grass');
  const B=[]; const tuft=(x,z)=>{ const n=3+Math.floor(Rn()*4), h0=0.08+0.1*Rn();
    for(let k=0;k<n;k++){ const bx=x+(Rn()-0.5)*0.07, bz=z+(Rn()-0.5)*0.07; B.push({x:bx,y:hAt(bx)-0.005,z:bz,h:h0*(0.6+0.6*Rn()),lean:(Rn()-0.5)*0.7,ry:Rn()*6.28,ph:Rn()*6.28}); } };
  for(let i=0;i<520;i++){ const x=-7+Rn()*20; tuft(x,1.5-Math.pow(Rn(),2)*0.5); }      // the near edge, in silhouette
  for(let i=0;i<260;i++){ const x=-7+Rn()*20; let z=-1.4+Rn()*2.6; if(Math.abs(z)<0.35) z+=z<0?-0.35:0.35; tuft(x,z); }   // scattered over the slope, off his path
  const m=new THREE.InstancedMesh(blade,mat,B.length); m.castShadow=false; m.receiveShadow=true; m.frustumCulled=false; scene.add(m);
  const o=new THREE.Object3D();
  return t=>{ for(let i=0;i<B.length;i++){ const b=B[i]; o.position.set(b.x,b.y,b.z);
      o.rotation.set(0.25*b.lean,b.ry,b.lean+0.07*Math.sin(t*1.3+b.x*0.9+b.ph*0.3)); o.scale.set(1,b.h,1); o.updateMatrix(); m.setMatrixAt(i,o.matrix); }
    m.instanceMatrix.needsUpdate=true; }; })();

// ---------------------------------------------------------------- a light rain the whole time, and a few stars: the night feels alive, lonely, heavy
const rainU={uT:{value:0}};
{ const Rn=rng(55), N=1300, pos=new Float32Array(N*2*3), sd=new Float32Array(N*2*4);
  for(let i=0;i<N;i++){ const x=-9+23*Rn(), z=-3+9*Rn(), ph=Rn()*14, sp=7+3*Rn(); for(let e=0;e<2;e++){ pos.set([x,0,z],(i*2+e)*3); sd.set([ph,sp,e,0.25+0.25*Rn()],(i*2+e)*4); } }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('sd',new THREE.BufferAttribute(sd,4));
  const m=new THREE.LineSegments(g,new THREE.ShaderMaterial({uniforms:rainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute vec4 sd; uniform float uT; varying float vA; void main(){ float y=13.0-mod(sd.x+sd.y*uT,14.5); float L=sd.w;
      vec3 p=position+vec3(-0.06*L*sd.z,y+L*sd.z,0.0); vA=sd.z; gl_Position=projectionMatrix*modelViewMatrix*vec4(p,1.0); }`,
    fragmentShader:`varying float vA; void main(){ gl_FragColor=vec4(vec3(0.62,0.66,0.74)*(0.03+0.07*vA),1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }
const starU={uT:{value:0},uH:{value:H}};
{ const Rn=rng(66), N=260, pos=new Float32Array(N*3), sd=new Float32Array(N*2);
  for(let i=0;i<N;i++){ pos.set([-40+90*Rn(),3+38*Rn(),-45],i*3); sd.set([Rn()*6.28,0.4+0.6*Rn()],i*2); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('sd',new THREE.BufferAttribute(sd,2));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:starU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute vec2 sd; uniform float uT,uH; varying float vA; void main(){ vA=sd.y*(0.65+0.35*sin(uT*1.7+sd.x)); gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); gl_PointSize=2.0+1.5*sd.y; }`,
    fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); gl_FragColor=vec4(vec3(0.9,0.92,1.0)*smoothstep(0.5,0.1,d)*vA*0.55,1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }

// ---------------------------------------------------------------- his face: two dot eyes, brows, a mouth. Sad under the sack, relieved as he lets go, smiling at the top.
// Drawn on the side of the head turned toward the camera (the film is a side view), so it reads in the wide shots too.
const FACE=(()=>{ const ink=new THREE.MeshBasicMaterial({color:0x1d1712}); const g=new THREE.Group(); scene.add(g);
  const eyeG=new THREE.SphereGeometry(1,12,8), eyes=[0,1].map(()=>{ const m=new THREE.Mesh(eyeG,ink); g.add(m); return m; });
  const browG=new THREE.CylinderGeometry(1,1,1,6); browG.rotateZ(Math.PI/2); const brows=[0,1].map(()=>{ const m=new THREE.Mesh(browG,ink); g.add(m); return m; });
  const mouthG=new THREE.TorusGeometry(1,0.16,6,24,Math.PI*0.75); mouthG.rotateZ(Math.PI+Math.PI*0.125); mouthG.translate(0,0.62,0);   // a shallow arc, centred: scale.y>0 smiles, <0 frowns
  const mouth=new THREE.Mesh(mouthG,ink); g.add(mouth);
  return (J,ex,yaw=0)=>{ const R0=0.13*HS; const u=J.head.clone().sub(J.neck).normalize(); const fw=rotY(V(1,0,0),yaw); const f=fw.sub(u.clone().multiplyScalar(fw.dot(u))).normalize();      // up of the head, and the way he faces
    const n=f.clone().multiplyScalar(0.62).add(V(0,0,0.78)).normalize(); const side=new THREE.Vector3().crossVectors(u,n).normalize();
    const at=(a,b,c)=>J.head.clone().addScaledVector(n,R0*a).addScaledVector(side,R0*b).addScaledVector(u,R0*c);
    const q=new THREE.Quaternion().setFromRotationMatrix(new THREE.Matrix4().makeBasis(side,u,n));
    [-1,1].forEach((sg,i)=>{ const e=eyes[i]; e.position.copy(at(0.93,0.34*sg,0.18)); e.quaternion.copy(q); e.scale.set(0.11*R0,0.15*R0*(ex>0.75?lerp(1,0.45,(ex-0.75)/0.25):1),0.06*R0);
      const b=brows[i]; b.position.copy(at(0.9,0.36*sg,0.5)); b.quaternion.copy(q).multiply(new THREE.Quaternion().setFromAxisAngle(V(0,0,1),-sg*0.45*clamp(-ex)));
      const bs=clamp(0.25-ex*0.9,0,1); b.scale.set(0.28*R0*bs+1e-4,0.035*R0,0.035*R0); });
    mouth.position.copy(at(0.95,0,-0.34)); mouth.quaternion.copy(q); const my=ex<0?lerp(-0.12,-0.55,-ex):lerp(-0.12,0.75,ex);
    mouth.scale.set(0.2*R0,0.2*R0*my,0.2*R0); }; })();
const faceEx=t=>{ if(t<TL.kneel1) return -1; if(t<TL.stand0) return lerp(-1,-0.15,sstep(TL.throws[0],TL.throws[STONE_N-1]+0.3,t));
  return lerp(lerp(-0.15,0.25,sstep(TL.stand0,TL.stand1,t)),1,sm5(sstep(T_ARR-0.3,T_ARR+0.7,t))); };

// ---------------------------------------------------------------- the sack and the stones
const sackMat=new THREE.MeshStandardMaterial({color:0x4a3f33,emissive:0x4a3f33,emissiveIntensity:0.01,roughness:1.0,map:SLD.noiseTex(256,4,150,40,40,0.08)});
SLD.rimify(sackMat,0xfff1d8,0.05,'sack');
const sack=new THREE.Mesh((()=>{ const g=new THREE.IcosahedronGeometry(1,5); const p=g.attributes.position; const Rn=rng(3);
  for(let i=0;i<p.count;i++){ const x=p.getX(i),y=p.getY(i),z=p.getZ(i); const k=1+0.035*Math.sin(x*5+y*3)+0.025*Math.sin(z*6-y*2)+(y<-0.4?-0.12*(y+0.4):0); p.setXYZ(i,x*k,y*k*(y<0?0.9:1.05),z*k); }
  g.computeVertexNormals(); return g; })(),sackMat);
sack.castShadow=true; sack.receiveShadow=true; scene.add(sack);
const neck=new THREE.Mesh(new THREE.CylinderGeometry(0.06,0.13,0.18,12),sackMat); neck.castShadow=true; scene.add(neck);   // gathered mouth
const STONE_N=TL.throws.length;
const stoneMat=new THREE.MeshStandardMaterial({color:0x9a958c,emissive:0x9a958c,emissiveIntensity:0.05,roughness:0.85,map:SLD.noiseTex(128,12,128,90,30,0.2)});
SLD.rimify(stoneMat,0xfff1d8,0.25,'stone');
const stones=[...Array(STONE_N)].map((_,i)=>{ const g=new THREE.IcosahedronGeometry(1,2); const p=g.attributes.position; const Rn=rng(40+i);
  for(let j=0;j<p.count;j++){ const k=0.85+0.3*Rn(); p.setXYZ(j,p.getX(j)*k,p.getY(j)*k*0.85,p.getZ(j)*k); } g.computeVertexNormals();
  const m=new THREE.Mesh(g,stoneMat); m.castShadow=true; m.receiveShadow=true; m.scale.setScalar(0.17+0.03*((i*7)%3)); m.userData.s0=m.scale.x; scene.add(m); return m; });

// ---------------------------------------------------------------- his path
const X_HOOK=-0.95, X_PEAK=2.55, X_BOTTOM=-0.75;                     // starts on the flat at the bottom, trudges up to about the middle of the hill (slowing as it steepens), then the slip takes him all the way back down
const climbU=u=>1-Math.pow(1-u,1.7);
const SLIPX=X_PEAK-X_BOTTOM;
const slipU=u=>u<0.6?0.55*Math.pow(u/0.6,2):0.55+0.45*(1-Math.pow(1-(u-0.6)/0.4,2));   // gathers speed down the slope, then skids out on the flat
const xCarry=t=>X_HOOK+(X_PEAK-X_HOOK)*climbU(clamp(t/TL.slip0))-SLIPX*slipU(clamp((t-TL.slip0)/(TL.slip1-TL.slip0)));
const XK=xCarry(TL.slip1);                                              // where he kneels
const WALK_V=2.5;
const X_STOP=PLAT.x-1.45;   // just short of the flag (FLAG.x-0.65): it waves at his right shoulder
const WALK_TAB=(()=>{ const dt=1/240, d=[0], ph=[0]; for(let k=1;k<240*8;k++){ const s=k*dt;
    const f=s<0.9?0.28:s<1.9?0.28+0.27*sm5(sstep(0.9,1.2,s)):0.55+0.45*sm5(sstep(1.9,2.5,s));   // two heavy steps, two easier ones, then he runs
    const v=WALK_V*f*Math.min(1,s/0.25), stride=lerp(0.75,1.5,(f-0.28)/0.72);
    d.push(d[k-1]+v*dt); ph.push(ph[k-1]+v/stride*2*Math.PI*dt); } return {d,ph}; })();
const walkLook=(t,a)=>{ const s=Math.max(0,t-TL.walk0); const i=Math.min(a.length-1,Math.floor(s*240)); return a[i]; };
function xWalk(t){ return Math.min(XK+walkLook(t,WALK_TAB.d),X_STOP); }
const T_ARR=(()=>{ let t=TL.walk0; while(xWalk(t)<X_STOP-1e-3&&t<DUR) t+=1/240; return t; })();
const xAt=t=>t<TL.walk0?xCarry(Math.min(t,TL.slip1)):xWalk(t);
const ground=x=>V(x,hAt(x),0);

// ---------------------------------------------------------------- poses
const CARRY={...P0,p:1.12,tilt:-0.22,aL:0.55,aR:0.2,kL:0.98,kR:0.78,dy:-0.02,sL:-0.2,sR:-0.2,eL:2.0,eR:2.0};
const KNEEL={...P0,p:0.45,tilt:0.2,aL:0.18,aR:0.05,kL:1.62,kR:1.55,dy:-0.03,sL:0.5,sR:0.5,eL:0.4,eR:0.4};   // upright on both knees, leaning to the sack
const STAND={...P0,p:0.04,tilt:-0.12,kL:0.06,kR:0.06};
const WALKUP={...P0,p:0.16,tilt:-0.1,kL:0.25,kR:0.25,eL:0.6,eR:0.6};
const LOOKUP={...P0,p:-0.06,tilt:-0.3,sL:0.55,sR:0.55,eL:0.15,eR:0.15,kL:0.04,kR:0.04};   // chest open, face lifted to the light
const ATPEACE={...P0,p:0.0,tilt:-0.08,sL:0.32,sR:0.22,eL:0.25,eR:0.3,kL:0.03,kR:0.03};   // the last pose: upright, head level, arms open and easy. Held still.
const thrownBy=t=>TL.throws.filter(x=>t>=x).length;
function heroAt(t){
  const x=xAt(t); let root=ground(x), yaw=0, P;
  if(t<TL.slip0){ const ph=(x-X_HOOK)/0.8*2*Math.PI+0.6; P=R.gait(CARRY,ph,0.85,0.3,0.55,0.05); P.p+=0.03*Math.sin(ph*2); }
  else if(t<TL.kneel0){ const u=sm5(sstep(TL.slip0,TL.slip1,t)); P=R.blend(CARRY,{...CARRY,p:1.15,tilt:-0.45,aL:-0.55,aR:-0.35,kL:0.15,kR:0.35,dy:0},Math.sin(Math.PI*Math.min(1,u*1.2)));   // feet trailing down the slope, chest to the hill
    P=R.blend(P,{...CARRY,p:1.05,kL:1.0,kR:0.9,dy:-0.12},sstep(TL.slip1-0.1,TL.kneel0,t)); }
  else { // kneel, and straighten a little with every stone
    const k=sm5(sstep(TL.kneel0,TL.kneel1,t)); const n=thrownBy(t)+ (t>=TL.throws[0]-0.6?0:0);
    const lighter=n/STONE_N; let base=R.blend({...CARRY,p:1.05,kL:1.0,kR:0.9,dy:-0.12},{...KNEEL,p:lerp(0.62,0.12,lighter),tilt:lerp(0.35,-0.1,lighter)},k);
    P=base;
    if(t>TL.stand0){ P=R.blend(P,STAND,sm5(sstep(TL.stand0,TL.stand1,t))); }
    if(t>TL.walk0){ const ph=walkLook(t,WALK_TAB.ph); const a=sstep(TL.walk0,TL.walk0+0.3,t)*(1-sstep(T_ARR-0.25,T_ARR+0.15,t));
      P=R.gait(R.blend(STAND,WALKUP,sstep(TL.walk0,TL.walk0+0.4,t)),ph,a,0.55,1.05,0.55); P.p+=0.08*a+0.22*(1-sstep(TL.walk0+0.7,TL.walk0+1.6,t))*a;   // still bowed for the first heavy steps
      if(t>T_ARR-0.2) P=R.blend(P,LOOKUP,sm5(sstep(T_ARR-0.2,T_ARR+0.8,t))); if(t>T_ARR+0.6) P=R.blend(P,ATPEACE,sm5(sstep(T_ARR+0.6,T_ARR+1.8,t)));
    yaw=-0.75*sm5(sstep(T_ARR+0.2,T_ARR+1.6,t)); } }   // he turns gently toward us, so the smile reads; then he is still, only the light moves
  // breathing
  P.p+=0.012*Math.sin(2*Math.PI*0.5*t)*(1-sstep(T_ARR+1.2,T_ARR+2.0,t));
  if(t>=TL.kneel0-0.05&&t<TL.stand1) return {root,yaw,P,x};   // kneeling on the flat at the bottom: knees on the ground is right
  const f=groundFix(P,root,yaw); return {root:f.root,yaw,P:f.P,x}; }
// Feet on a 50-degree slope: the rig stands both feet at the root height, so the uphill foot sank into the hill (most
// visibly in the slide). Keep the body on the surface and bend any leg that would go into the slope until its foot and knee sit on it.
function groundFix(P,root,yaw){ let J; P={...P};
  for(let it=0;it<24;it++){ J=R.skel(P,root,yaw); let ok=true;
    for(const s of ['L','R']){ const f=J['f'+s], k=J['k'+s]; const pen=Math.max(hAt(f.x)+0.012-f.y,hAt(k.x)+0.04-k.y);
      if(pen>0.004&&P['k'+s]<2.3){ ok=false; P['k'+s]=Math.min(2.3,P['k'+s]+Math.min(0.35,pen*2.6)); P['a'+s]=Math.min(1.9,P['a'+s]+Math.min(0.22,pen*1.5)); } }   // capped: a runaway bend folds the leg backwards
    if(ok) break; }
  // safety net: if a foot or knee is still in the slope, lift the whole body just clear of it
  J=R.skel(P,root,yaw); let lift=0; for(const s of ['L','R']) lift=Math.max(lift,hAt(J['f'+s].x)+0.012-J['f'+s].y,hAt(J['k'+s].x)+0.04-J['k'+s].y);
  if(lift>0){ root=root.clone(); root.y+=lift; }
  return {P,root}; }

// ---------------------------------------------------------------- sack placement
const SACK_R0=0.5;
function sackScale(t){ return 1-0.13*thrownBy(t)-0.06*sstep(TL.throws[STONE_N-1],TL.throws[STONE_N-1]+0.5,t); }
const SACK_GROUND=x=>V(x,hAt(x),-0.4);   // set down beside him on the far side, so it never hides him
function sackAt(t,J){ const s=sackScale(t)*SACK_R0;
  // on his back: above the torso, behind the shoulders
  const back=J.neck.clone().lerp(J.hip,0.42); const up=J.neck.clone().sub(J.hip).normalize(); const nrm=V(-up.y,up.x,0).normalize(); // torso normal in the x-y plane
  const onBack=back.clone().addScaledVector(nrm.y>0?nrm:nrm.negate(),s*0.95).add(V(0,0,0));
  const gx=XK+0.55; const onGround=SACK_GROUND(gx).add(V(0,s*0.82,0));
  const u=sm5(sstep(TL.sackDrop-0.25,TL.sackDrop+0.2,t)); const p=onBack.clone().lerp(onGround,u); p.y+=0.25*Math.sin(Math.PI*u)*(1-u);
  return {p,s,on:1-u}; }

// ---------------------------------------------------------------- stones: out of the sack, shown, thrown backwards down the hill, rolling into the dark
const STONE_V=V(-2.2,1.55,0.12), G=9.8;
const STONE_SIM=TL.throws.map((T,i)=>{ // precomputed flight + roll (pure lookups)
  const r=stones[i].scale.x; const kneel={...KNEEL,p:lerp(0.62,0.12,i/STONE_N),tilt:lerp(0.35,-0.1,i/STONE_N)};
  const J=R.skel(kneel,ground(XK),0); const p0=J.shR.clone().add(V(-0.25,0.32,0.05)); const out=[]; let p=p0.clone(), v=STONE_V.clone().multiplyScalar(1+0.06*(i%2)); let rolling=false, ang=0, dt=1/240;
  for(let k=0;k<240*7;k++){ out.push([p.x,p.y,p.z,ang]);
    if(!rolling){ v.y-=G*dt; p.addScaledVector(v,dt); const hy=hAt(p.x)+r*0.85; if(p.y<=hy){ p.y=hy; rolling=true; v.y=0; v.x*=0.7; } }
    else { const s=slopeAt(p.x); const ax=-G*s/(1+s*s)-0.6*Math.sign(v.x)*(Math.abs(v.x)>0.05?1:0); v.x+=ax*dt; v.x*=1-0.15*dt; p.x+=v.x*dt; p.y=hAt(p.x)+r*0.85; p.z+=v.z*dt*0.3; }
    ang+=Math.hypot(v.x,v.y)*dt/r; }
  return {p0,out}; });
function stoneAt(i,t,J){ const T=TL.throws[i];
  if(t<T-0.62) return null;                                             // still in the sack
  if(t<T){ // out of the sack mouth, up in front of his chest (readable), then wound back over the shoulder
    const sk=sackAt(t,J); const mouth=sk.p.clone().add(V(0,sk.s*0.9,0)); const show=J.neck.clone().add(V(0.42,0.12,0.18)); const back=STONE_SIM[i].p0;
    const u1=sm5(sstep(T-0.62,T-0.3,t)), u2=sstep(T-0.16,T,t);
    return {p:mouth.clone().lerp(show,u1).lerp(back,u2*u2),ang:0,inHand:true}; }
  if(t>T+0.55) return null;                                             // crumbled to dust in the air
  const f=Math.min(STONE_SIM[i].out.length-1,Math.floor((t-T)*240)); const o=STONE_SIM[i].out[f]; return {p:V(o[0],o[1],o[2]),ang:o[3],inHand:false,k:1-sstep(T+0.22,T+0.55,t)}; }
// the dust each stone breaks into: drifts back and up, glows faintly, gone in a second
const dustU={uT:{value:0},uH:{value:H}};
{ const Rn=rng(91), N=70, pos=new Float32Array(STONE_N*N*3), sd=new Float32Array(STONE_N*N*4);
  TL.throws.forEach((T,i)=>{ const o=STONE_SIM[i].out[Math.floor(0.3*240)];
    for(let k=0;k<N;k++){ const j=i*N+k; pos.set([o[0],o[1],o[2]],j*3); sd.set([T+0.24+0.12*Rn(),(Rn()-0.75)*1.3,(Rn()-0.2)*1.0,(Rn()-0.5)*0.8],j*4); } });
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('sd',new THREE.BufferAttribute(sd,4));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:dustU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute vec4 sd; uniform float uT,uH; varying float vA;
      void main(){ float a=uT-sd.x; vA=a<0.0?0.0:(1.0-smoothstep(0.2,1.1,a)); vec3 p=position+vec3(sd.y,sd.z,sd.w)*(1.0-exp(-a*2.5))+vec3(-0.15,0.25,0.0)*a;
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; gl_PointSize=a<0.0?0.0:clamp(0.035*uH/(-mv.z),1.0,24.0); }`,
    fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vec3(0.95,0.85,0.7)*a*vA*0.9,1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }

// ---------------------------------------------------------------- the flag at the top (NEW LIFE), waving gently in the lamp's light
const FLAG=V(PLAT.x-0.8,HH,-0.5);   // just in from the crest, behind his path: in the opening wide shot, and he stops right beside it
{ const pole=new THREE.Mesh(new THREE.CylinderGeometry(0.022,0.03,2.0,12),SLD.rimify(new THREE.MeshStandardMaterial({color:0xb9b2a4,metalness:0.3,roughness:0.45}),0xfff1d8,0.2,'pole'));
  pole.position.copy(FLAG).add(V(0,1.0,0)); pole.castShadow=true; scene.add(pole); }
const flagGeo=new THREE.PlaneGeometry(0.95,0.56,24,10); flagGeo.translate(0.475,0,0); const FLAG0=flagGeo.attributes.position.array.slice();
const flag=new THREE.Mesh(flagGeo,new THREE.MeshStandardMaterial({color:PAL.GOLD,emissive:PAL.GOLD,emissiveIntensity:0.18,roughness:0.7,side:THREE.DoubleSide}));
flag.position.copy(FLAG).add(V(0.02,1.72,0)); flag.castShadow=true; scene.add(flag);
function waveFlag(t){ const p=flagGeo.attributes.position; const g=1+0.8*sstep(TL.glow0,TL.glow0+0.6,t);
  for(let i=0;i<p.count;i++){ const x=FLAG0[i*3], y=FLAG0[i*3+1]; const k=x/0.95;
    p.setXYZ(i,x*(1-0.06*k),y-0.05*k*k+0.045*g*k*Math.sin(x*7-t*5.5),0.13*g*k*Math.sin(x*8-t*6.5+y*2)+0.04*k*Math.sin(t*3.1+y*5)); }   // ripples you can read from the side, not only in the shading
  p.needsUpdate=true; flagGeo.computeVertexNormals(); }

// ---------------------------------------------------------------- the enlightenment: a slow sunburst behind him, a halo, rising gold motes, a warm glow on him
const RAYS=new THREE.Group(); scene.add(RAYS); S.NOREFL.push(RAYS);
const rayU={uA:{value:0}};
{ const Rn=rng(77); for(let i=0;i<22;i++){ const len=2.2+2.4*Rn(), w=0.05+0.12*Rn(); const g=new THREE.PlaneGeometry(w,len); g.translate(0,len/2,0);
    const m=new THREE.Mesh(g,new THREE.ShaderMaterial({uniforms:{uA:rayU.uA,uS:{value:Rn()}},transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,side:THREE.DoubleSide,fog:false,
      vertexShader:`varying vec2 vU; void main(){ vU=uv; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
      fragmentShader:`uniform float uA,uS; varying vec2 vU; void main(){ float a=pow(1.0-vU.y,1.8)*exp(-pow((vU.x-0.5)*3.2,2.0))*uA*(0.55+0.45*uS); gl_FragColor=vec4(vec3(1.0,0.78,0.42)*a*0.32,1.0); }`}));
    m.rotation.z=i/22*Math.PI*2+0.15*(Rn()-0.5); RAYS.add(m); } }
const halo=SLD.glowSprite(scene,0xffd27a,0); const halo2=SLD.glowSprite(scene,0xffb24a,0); S.NOREFL.push(halo,halo2);
const sun=SLD.glowSprite(scene,0xffd08a,0), sunCore=SLD.glowSprite(scene,0xfff0c8,0), sky=SLD.glowSprite(scene,0xff9a4a,0); S.NOREFL.push(sun,sunCore,sky);
const riseU={uT:{value:0},uH:{value:H},uO:{value:V(0,0,0)},uA:{value:0}};
{ const Rn=rng(31), N=420, pos=new Float32Array(N*3), sd=new Float32Array(N*4);
  for(let i=0;i<N;i++){ const a=Rn()*6.283, r=0.15+0.9*Math.sqrt(Rn()); pos.set([Math.cos(a)*r,Rn()*0.4,Math.sin(a)*r*0.6],i*3); sd.set([0.25+0.6*Rn(),Rn()*6.28,0.6+0.8*Rn(),Rn()*2.4],i*4); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.BufferAttribute(pos,3)); g.setAttribute('sd',new THREE.BufferAttribute(sd,4));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:riseU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute vec4 sd; uniform float uT,uH,uA; uniform vec3 uO; varying float vA;
      void main(){ float tt=max(0.0,uT-sd.w*0.5); float life=mod(tt*sd.x*0.6,3.0); vec3 p=uO+position+vec3(0.12*sin(uT*sd.z+sd.y),life*1.1,0.1*cos(uT*sd.z*0.7+sd.y));
        vA=uA*smoothstep(0.0,0.4,life)*(1.0-smoothstep(1.8,3.0,life)); vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv;
        gl_PointSize=clamp(0.03*uH/(-mv.z),1.0,30.0); }`,
    fragmentShader:`varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vec3(1.0,0.82,0.5)*a*a*vA,1.0); }`}));
  m.frustumCulled=false; scene.add(m); S.NOREFL.push(m); }
function enlighten(t,J){ const e=sm5(sstep(TL.glow0,TL.glow1,t)); const c=J.neck.clone().lerp(J.hip,0.3);
  RAYS.position.copy(c).add(V(0,0,-0.7)); RAYS.rotation.z=0.06*t; RAYS.scale.setScalar(0.6+0.5*e); rayU.uA.value=0.22*e;   // only a hint of rays now: the sunrise does the work
  const r=sm5(sstep(TL.glow0-0.3,DUR,t)), sp=V(PLAT.x-0.4,HH-1.0+3.4*r,-9);    // the sun comes up slowly behind the hilltop and keeps rising to the end
  sun.position.copy(sp); sun.scale.setScalar(13); sun.material.opacity=0.5*e; sunCore.position.copy(sp); sunCore.scale.setScalar(4.2); sunCore.material.opacity=0.85*e;
  sky.position.copy(sp).add(V(0,-1,-2)); sky.scale.setScalar(42); sky.material.opacity=0.2*e;
  halo.position.copy(c).add(V(0,0.2,-0.3)); halo.scale.setScalar(1.2+0.8*e); halo.material.opacity=0.1*e;
  halo2.position.copy(c).add(V(0,0.3,-0.6)); halo2.scale.setScalar(3.5*e+0.1); halo2.material.opacity=0.08*e;
  riseU.uT.value=t; riseU.uO.value.copy(J.hip).setY(J.hip.y-0.9); riseU.uA.value=0.5*e; rainU.uT.value=t; starU.uT.value=t; dustU.uT.value=t;
  hero.mat.emissiveIntensity=0.035+0.12*e; hero.mat.emissive.set(0xede6d6).lerp(new THREE.Color(0xffc670),e); hero.mat.userData.rim.value=0.2+0.45*e;
  waveFlag(t); GRASS(t); }

// ---------------------------------------------------------------- camera: wide side view of the climb; push in for the letting go; follow him up into the light
const WIDE={p:V(2.95,4.6,25.5),l:V(2.85,4.4,0)};   // the whole hill, him small at the bottom, the lamp at the top
function camAt(t){ const J0=ground(XK);
  const close={p:V(XK+0.35,J0.y+1.45,6.8),l:V(XK+0.25,J0.y+0.95,0)};   // a touch ahead of him so his face reads   // centred on him for the fall and the letting go
  const top={p:V(PLAT.x-1.75,HH+2.0,10.5),l:V(PLAT.x-1.25,HH+2.3,0)};
  let p=WIDE.p.clone(), l=WIDE.l.clone();
  const u1=sm5(sstep(TL.push0,TL.push1,t)); p.lerp(close.p,u1); l.lerp(close.l,u1);
  if(t>TL.pull0){ // pull back and follow him up the hill, ending framed on the plateau and the lamp
    const x=xAt(t); const follow={p:V(x+0.9,hAt(x)+2.4,11.5),l:V(x+0.6,hAt(x)+1.4,0)};
    const u2=sm5(sstep(TL.pull0,TL.pull1,t)); p.lerp(follow.p,u2); l.lerp(follow.l,u2);
    const u3=sm5(sstep(T_ARR-0.6,T_ARR+1.2,t)); p.lerp(top.p,u3); l.lerp(top.l,u3); }
  // a slow drift so the hold never feels frozen
  p.x+=0.12*Math.sin(t*0.23); return {p,l}; }

// ---------------------------------------------------------------- one sub-frame
let LAST={};
function setT(t){
  const h=heroAt(t); let P=h.P; let J=R.skel(P,h.root,h.yaw);
  const sk=sackAt(t,J);
  // hands: hold the sack mouth over the shoulders while carrying; reach into the sack and throw while kneeling
  const ws=[];
  if(sk.on>0.02){ const top=sk.p.clone().add(V(0.12,sk.s*0.75,0)); P={...P,tL:top.clone().add(V(0,0,0.14)),tR:top.clone().add(V(0,0,-0.14)),wL:sk.on,wR:sk.on,pL:V(-0.5,-0.5,0.7),pR:V(-0.5,-0.5,-0.7)}; }
  let held=null;
  for(let i=0;i<STONE_N;i++){ const s=stoneAt(i,t,J); if(!s){ stones[i].visible=false; continue; }
    stones[i].visible=true; stones[i].position.copy(s.p); stones[i].rotation.set(0,0,s.ang); stones[i].scale.setScalar(stones[i].userData.s0*(s.k??1));
    if(s.inHand) held=s.p; }
  if(t>TL.kneel1-0.2&&t<TL.stand1){ // left hand rests on the sack, right hand works the stones
    const sk2=sackAt(t,J); const rest=sk2.p.clone().add(V(-0.05,sk2.s*0.85,0.18));
    const tw=held?1:0.6; P={...P,tL:rest,wL:0.8,pL:V(-0.4,-0.6,0.7),tR:held||sk2.p.clone().add(V(0,sk2.s*1.0,-0.05)),wR:tw,pR:V(-0.6,-0.3,-0.7)};
    // twist the shoulders back as he winds up each throw
    const tws=TL.throws.reduce((a,T)=>a+Math.exp(-Math.pow((t-T+0.08)/0.16,2)),0); P.ty=(P.ty||0)+0.75*tws; P.hy=(P.hy||0)+0.5*tws; }
  J=R.skel(P,h.root,h.yaw); R.poseFig(hero,J); FACE(J,faceEx(t),h.yaw);
  sack.position.copy(sk.p); sack.scale.set(sk.s,sk.s*0.95,sk.s*0.9);
  const tilt=sk.on>0.5?Math.atan2(J.neck.y-J.hip.y,J.neck.x-J.hip.x)-Math.PI/2:0; sack.rotation.set(0,0,tilt*sk.on*0.6);
  neck.position.copy(sk.p).add(V(0.0,sk.s*1.0,0)); neck.scale.setScalar(Math.max(0.35,sk.s/SACK_R0));
  // camera
  const c=camAt(t); cam.position.copy(c.p); cam.lookAt(c.l);
  // the lamp blooms when he steps into it
  const pay=0.32*sm5(sstep(TL.bloom0,TL.bloom1,t));
  enlighten(t,J); keyAt(t,J);
  S.tick(t,pay);
  LAST={J}; return {J,h}; }

// ---------------------------------------------------------------- render
const acc=document.createElement('canvas'); acc.width=W; acc.height=H; const actx=acc.getContext('2d');
window.renderAt=function(t,Ksub=3){ let K=Ksub, sh=1/60;
  if(TL.throws.some(T=>t>T-0.15&&t<T+0.35)||(t>TL.slip0&&t<TL.slip1)) K=Math.max(Ksub,5);
  actx.globalAlpha=1; actx.clearRect(0,0,W,H);
  for(let k=0;k<K;k++){ const tt=clamp(t+(K>1?(k/(K-1)-0.5)*sh:0),0,DUR-1e-4); setT(tt); S.renderer.shadowMap.needsUpdate=true; S.composer.render(); actx.globalAlpha=1/(k+1); actx.drawImage(S.renderer.domElement,0,0); }
  return acc.toDataURL('image/jpeg',0.95); };
const proj=v=>{ const p=v.clone().project(cam); return [p.x*0.5+0.5,0.5-p.y*0.5,p.z<1?1:0]; };
window.metaAt=function(t){ const s=setT(t); cam.updateMatrixWorld(); const o={t};
  o.stones=stones.map(m=>m.visible?proj(m.position.clone().add(V(0,0.32,0))):null);
  o.oldLife=proj(V(-0.5,-0.35,1.6));   // OLD LIFE sits just under him on the ground edge at the start
  o.newLife=proj(V(FLAG.x+0.35,HH+2.25,0.2)); o.newLifeWide=proj(V(PLAT.x-1.3,HH+0.45,1.5)); o.hero=proj(s.J.head);
  // arrow targets: where the place names point (his start spot at the foot of the hill, the hilltop, the flag)
  o.oldPt=proj(V(X_HOOK,0.05,1.5)); o.newPtWide=proj(V(FLAG.x+0.3,HH+1.75,-0.5)); o.newPt=proj(V(FLAG.x,HH+1.3,0.25));
  return o; };
window.events={...TL,XK,T_ARR};
window.ready=true;
