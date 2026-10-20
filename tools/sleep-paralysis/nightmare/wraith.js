// The wraith: a rigged, towering humanoid made of tangled black branches, torn ink cloth and crimson filaments.
// Every animated joint is a Group with unit scale; meshes ride rigidly on their bone and only twigs drift.
import * as T from 'three';
import {rng,V,TubeBuilder,branch,walk,patchGrowth,clamp,smooth,lerp} from './lib.js';

const INK_FRAG=`gl_FragColor.rgb*= .75+ .35*vShade;`;
const CRIMSON_FRAG=`
 float ph=fract(uTime*.23+vSeed*5.13); float d=vArc-ph; float d2=vArc-fract(ph+.5);
 float pulse=exp(-d*d/.0016)+.55*exp(-(d+.05)*(d+.05)/.004)+.6*exp(-d2*d2/.0016);
 vec3 blood=vec3(.40,.018,.02);
 gl_FragColor.rgb=mix(gl_FragColor.rgb, blood*(.35+uPulseGain*1.6*pulse), .12+.8*clamp(pulse*uPulseGain,0.,1.));
`;

function clothTexture(seed){
 const c=document.createElement('canvas');c.width=256;c.height=512;const x=c.getContext('2d'),R=rng(seed);
 x.clearRect(0,0,256,512);
 // vertical shreds with torn ragged ends
 for(let i=0;i<26;i++){const cx=R()*256,w=6+R()*30,end=200+R()*312;x.beginPath();x.moveTo(cx-w/2,0);
  for(let y=0;y<=end;y+=8){x.lineTo(cx-w/2+Math.sin(y*.05+i)*4+(R()-.5)*5,y);}
  x.lineTo(cx+(R()-.5)*6,end+20+R()*40);
  for(let y=end;y>=0;y-=8){x.lineTo(cx+w/2+Math.sin(y*.045+i*2)*4+(R()-.5)*5,y);}
  x.closePath();const g=x.createLinearGradient(0,0,0,end);const v=60+R()*80;g.addColorStop(0,`rgba(${v},${v},${v},0)`);g.addColorStop(.12,`rgba(${v},${v},${v},.9)`);g.addColorStop(.75,`rgba(${v*.8},${v*.8},${v*.8},.75)`);g.addColorStop(1,`rgba(${v*.6},${v*.6},${v*.6},0)`);x.fillStyle=g;x.fill();}
 // engraved fibres
 x.globalCompositeOperation='source-atop';
 for(let i=0;i<900;i++){const a=R()*256,b=R()*512;x.strokeStyle=`rgba(${R()<.5?10:200},${R()<.5?10:200},${R()<.5?10:200},${.05+R()*.12})`;x.lineWidth=.6;x.beginPath();x.moveTo(a,b);x.lineTo(a+(R()-.5)*4,b+10+R()*40);x.stroke();}
 for(let i=0;i<500;i++){x.fillStyle=`rgba(0,0,0,${.2+R()*.5})`;const a=R()*256,b=R()*512,s=1+R()*4;x.fillRect(a,b,s,s*(1+R()*2));}
 // a few crimson fissures in the recesses
 for(let i=0;i<5;i++){x.strokeStyle='rgba(120,8,8,.7)';x.lineWidth=.8+R();x.beginPath();let a=R()*256,b=R()*300;x.moveTo(a,b);for(let k=0;k<8;k++){a+=(R()-.5)*14;b+=8+R()*16;x.lineTo(a,b);}x.stroke();}
 const t=new T.CanvasTexture(c);t.colorSpace=T.SRGBColorSpace;t.anisotropy=4;return t;
}

function growthAttrs(geo,swayFn){
 const p=geo.attributes.position,n=p.count,cen=new Float32Array(n*3),arc=new Float32Array(n),grow=new Float32Array(n*2),sway=new Float32Array(n),seed=new Float32Array(n),shade=new Float32Array(n);
 for(let i=0;i<n;i++){cen[i*3]=p.getX(i);cen[i*3+1]=p.getY(i);cen[i*3+2]=p.getZ(i);grow[i*2]=-99;grow[i*2+1]=1;sway[i]=swayFn(p.getX(i),p.getY(i),p.getZ(i));shade[i]=.5;}
 geo.setAttribute('aCenter',new T.BufferAttribute(cen,3));geo.setAttribute('aArc',new T.BufferAttribute(arc,1));geo.setAttribute('aGrow',new T.BufferAttribute(grow,2));
 geo.setAttribute('aSway',new T.BufferAttribute(sway,1));geo.setAttribute('aSeed',new T.BufferAttribute(seed,1));geo.setAttribute('aShade',new T.BufferAttribute(shade,1));return geo;
}

export class Wraith{
 constructor(scene,opts={}){
  this.uniforms={uTime:{value:0},uSwayAmp:{value:.016},uGrowShift:{value:0},uPulseGain:{value:1}};
  const u=this.uniforms;
  this.ink=patchGrowth(new T.MeshBasicMaterial({color:new T.Color(.018,.017,.018),fog:true}),u,INK_FRAG);
  this.crimson=patchGrowth(new T.MeshBasicMaterial({color:new T.Color(.3,.02,.02),fog:true}),u,CRIMSON_FRAG);
  this.depth=patchGrowth(new T.MeshDepthMaterial({depthPacking:T.RGBADepthPacking}),u);
  this.root=new T.Group();this.root.name='WraithRoot';scene.add(this.root);
  this.bones={};this.meshes=[];this.R=rng(opts.seed||90210);
  this.build();
 }
 bone(name,parent,pos){const g=new T.Group();g.name=name;g.position.copy(pos);(parent?this.bones[parent]:this.root).add(g);this.bones[name]=g;g.userData.rest=pos.clone();return g;}
 attach(name,B,mat){if(!B.n)return;const m=new T.Mesh(B.geometry(),mat);m.frustumCulled=false;m.castShadow=mat===this.ink;m.customDepthMaterial=this.depth;this.bones[name].add(m);this.meshes.push(m);}
 // A limb: a bundle of twisted ligament strands around an axis from a to b (local space of its bone),
 // with an elliptical envelope, a dark core, crimson veins and outward twigs.
 limb(name,a,b,o){
  const R=this.R,B=new TubeBuilder(),C=new TubeBuilder();const axis=V().subVectors(b,a),L=axis.length();axis.normalize();
  const side=Math.abs(axis.y)<.9?V(0,1,0):V(1,0,0);const u1=V().crossVectors(axis,side).normalize(),u2=V().crossVectors(axis,u1).normalize();
  const env=o.env||(s=>.05),ex=o.ex||1,ez=o.ez||1;
  const at=(s,ph,rr)=>{const r=env(s)*rr;return V().copy(a).addScaledVector(axis,s*L).addScaledVector(u1,Math.cos(ph)*r*ex).addScaledVector(u2,Math.sin(ph)*r*ez);};
  // core mass (keeps the silhouette solid)
  const core=[];for(let i=0;i<=16;i++){const s=-.06+i/16*1.12;core.push(at(s,0,0));}
  B.tube(core,s=>env(-.06+s*1.12)*(o.coreK??.55),{sides:7,shade:.1});
  const nS=o.strands??18;
  for(let k=0;k<nS;k++){const ph0=R()*Math.PI*2,tw=(R()-.5)*(o.twist??5),rr=.55+R()*.55,s0=-.08-R()*.06,s1=1.04+R()*.08;const pts=[];
   for(let i=0;i<=22;i++){const s=s0+(s1-s0)*i/22;const p=at(s,ph0+tw*s,rr*(1+.18*Math.sin(s*9+k)));p.x+=(R()-.5)*.006;p.z+=(R()-.5)*.006;pts.push(p);}
   const thick=(o.strandR??.011)*(.45+R()*.9);B.tube(pts,s=>thick*(.55+.45*Math.sin(Math.PI*clamp(s))),{shade:R(),sides:5});
   if(R()<(o.veinP??.25)){const vp=pts.map(p=>p.clone().addScaledVector(V().subVectors(p,a).projectOnPlane(axis).normalize(),thick*.9));C.tube(vp,s=>.0016*(1-.5*s),{seed:R(),sides:3});}
  }
  // twigs and thorny offshoots
  const nT=o.twigs??10;
  for(let k=0;k<nT;k++){const s=.08+R()*.9,ph=R()*Math.PI*2;const p=at(s,ph,.9);const out=V().subVectors(p,at(s,0,0)).normalize();
   const dir=out.clone().multiplyScalar(.8).addScaledVector(o.twigBias||V(),1).addScaledVector(axis,(R()-.5)*.6).normalize();
   const len=(o.twigLen??.35)*(.4+R()*.9);
   branch(B,R,p,dir,len,(o.twigR??.006)*(.6+R()*.6),o.twigDepth??2,{bias:o.twigBias||V(),birth:o.twigBirth?o.twigBirth(R):-99,dur:o.twigDur??1.5,sway0:.15,swayPerM:1.6,kids:2.4,spreadMin:20,spreadMax:55,lenK:.55,radK:.6});}
  // loose torn filaments that hang or float from the limb
  const nF=o.filaments??6;
  for(let k=0;k<nF;k++){const s=R(),ph=R()*Math.PI*2,p=at(s,ph,1);const pts=walk(R,p,V(0,-1,0).add(V((R()-.5)*.6,0,(R()-.5)*.6)),.15+R()*.4,{jag:.5});B.tube(pts,a=>.0022*(1-a*.8),{sway0:.3,sway1:1.2,seed:R(),sides:3});}
  this.attach(name,B,this.ink);this.attach(name,C,this.crimson);
 }
 build(){
  const R=this.R;
  // skeleton (local: +y up, faces +z). Lengths in metres; root is scaled uniformly once in the scene.
  this.bone('pelvis',null,V(0,1.32,0));
  this.bone('spine','pelvis',V(0,0,0));
  this.bone('neck','spine',V(0,.86,.02));
  this.bone('head','neck',V(0,.2,.16));
  for(const s of [-1,1]){const sd=s<0?'L':'R';
   this.bone('shoulder'+sd,'spine',V(s*.29,.8,.0));this.bone('elbow'+sd,'shoulder'+sd,V(0,-.8,0));this.bone('wrist'+sd,'elbow'+sd,V(0,-.76,0));
   this.bone('hip'+sd,'pelvis',V(s*.115,0,0));this.bone('knee'+sd,'hip'+sd,V(0,-.68,0));
  }
  // torso: long, narrow, rib-like cage tapering into a wasp waist
  this.limb('spine',V(0,-.05,0),V(0,.9,.02),{env:s=>.06+.075*smooth(.2,.75,s)-.04*smooth(.82,1,s),ex:1.55,ez:.95,strands:34,strandR:.012,twist:2.2,veinP:.22,
   twigs:14,twigBias:V(0,.35,0),twigLen:.4,twigR:.007,filaments:16});
  // neck stem bowed forward
  this.limb('neck',V(0,-.04,0),V(0,.2,.17),{env:s=>.035,strands:12,strandR:.008,twist:3,veinP:.3,twigs:4,twigLen:.25,twigBias:V(0,.6,-.3),filaments:3});
  // head: an obscured, heavy skull mass of dark tangles; no features
  {const B=new TubeBuilder(),C=new TubeBuilder();const skull=new T.SphereGeometry(1,24,18);skull.scale(.095,.125,.19);skull.rotateX(.15);skull.translate(0,.05,.08);
   const m=new T.Mesh(growthAttrs(skull,()=>0),this.ink);m.castShadow=true;m.customDepthMaterial=this.depth;this.bones.head.add(m);this.meshes.push(m);
   const jaw=new T.SphereGeometry(1,18,12);jaw.scale(.055,.045,.11);jaw.rotateX(.9);jaw.translate(0,-.06,.2);const mj=new T.Mesh(growthAttrs(jaw,()=>0),this.ink);this.bones.head.add(mj);this.meshes.push(mj);
   // wrapping tangles over the skull
   for(let k=0;k<28;k++){const th=R()*Math.PI*2,ph=Math.acos(2*R()-1);const p=V(Math.sin(ph)*Math.cos(th)*.12,.06+Math.cos(ph)*.14,.06+Math.sin(ph)*Math.sin(th)*.15);
    const t=V(-Math.sin(th),R()-.5,Math.cos(th)).normalize();const pts=[];for(let i=0;i<9;i++){const q=p.clone().addScaledVector(t,(i-4)*.025);q.sub(V(0,.06,.06)).multiplyScalar(1.0+R()*.03).add(V(0,.06,.06));pts.push(q);}
    B.tube(pts,s=>.004*(.4+Math.sin(Math.PI*s)),{sides:3,shade:R()});}
   for(let k=0;k<6;k++){const p=V((R()-.5)*.1,.1+R()*.08,.04+R()*.12);const pts=walk(R,p,V((R()-.5),.3,(R()-.2)),.25,{jag:.4});C.tube(pts,s=>.0015,{seed:R(),sides:3});}
   // crown: the antler-like canopy of dead branches spreading up and out, partly growing during the film
   for(let k=0;k<17;k++){const th=(k/17)*Math.PI*2+R()*.3;const p=V(Math.cos(th)*.08,.12+R()*.06,.02+Math.sin(th)*.08-.03);
    const dir=V(Math.cos(th)*.9,1.1+R()*.5,Math.sin(th)*.6-.35).normalize();const big=k%3===0;
    const birth=big?.2+k*.32:-99;
    branch(B,R,p,dir,big?1.5+R()*.6:.6+R()*.6,big?.016:.01,big?4:3,{bias:V(0,.15,0),birth,dur:big?3.2:1,sway0:.05,swayPerM:.8,kids:3,spreadMin:18,spreadMax:50,lenK:.56,radK:.62,durK:.6});}
   this.attach('head',B,this.ink);this.attach('head',C,this.crimson);}
  // shoulders sprout the second canopy: long branches reaching sideways like the reference
  for(const s of [-1,1]){const sd=s<0?'L':'R';
   const B=new TubeBuilder();for(let k=0;k<5;k++){const p=V((R()-.5)*.08,(R()-.5)*.06,(R()-.5)*.06);const dir=V(s*(.7+R()*.4),.9+R()*.8,(R()-.7)*.8).normalize();
    branch(B,R,p,dir,.8+R()*.8,.011,3,{bias:V(0,.12,0),birth:k<3?1.5+k*2.2+(s>0?1.1:0):-99,dur:3,sway0:.05,swayPerM:1,kids:3,lenK:.55,radK:.6});}
   this.attach('shoulder'+sd,B,this.ink);
   const arm={strands:12,strandR:.0075,twist:4,veinP:.12,twigs:7,twigBias:V(0,-.5,0),twigLen:.3,twigR:.005,filaments:8};
   this.limb('shoulder'+sd,V(0,.04,0),V(0,-.8,0),{...arm,env:s=>.042-.012*s+.01*Math.sin(Math.PI*s)});
   this.limb('elbow'+sd,V(0,.02,0),V(0,-.76,0),{...arm,env:s=>.034-.014*s+.008*Math.sin(Math.PI*s),strands:12});
   this.limb('hip'+sd,V(0,.04,0),V(0,-.68,.02),{env:s=>.034-.012*s,strands:12,strandR:.008,twist:3,veinP:.2,twigs:5,twigBias:V(0,-.6,0),filaments:7});
   this.limb('knee'+sd,V(0,.02,.02),V(0,-.66,-.02),{env:s=>.024-.012*s+.02*smooth(.9,1.05,s),strands:11,strandR:.007,twist:2,veinP:.2,twigs:6,twigBias:V(0,-.8,0),filaments:6});
   this.hand(sd,s);
   // roots: the feet dissolve into tendrils spreading over the floor
   const F=new TubeBuilder();for(let k=0;k<16;k++){const th=R()*Math.PI*2;const p=V(Math.cos(th)*.03,-.6,Math.sin(th)*.03);const pts=walk(R,p,V(Math.cos(th),-.35,Math.sin(th)),.25+R()*.5,{jag:.35,bias:V(0,-.3,0)});
    for(const q of pts)q.y=Math.max(q.y,-.655);F.tube(pts,a=>.007*(1-a*.9),{sides:4});}
   this.attach('knee'+sd,F,this.ink);
  }
  this.cloth();
  this.fingerRest();
 }
 hand(sd,s){
  const R=this.R,w=this.bones['wrist'+sd];const B=new TubeBuilder(),C=new TubeBuilder();
  // narrow palm
  for(let k=0;k<14;k++){const x0=(R()-.5)*.08,pts=[V(x0*.5,.02,0),V(x0,-.1,(R()-.5)*.025),V(x0*1.3,-.22,(R()-.5)*.02)];B.tube(pts,s=>.012*(1-.3*s),{shade:R(),sides:5});}
  if(R()<1)C.tube([V(.005,0,.012),V(.012,-.09,.014),V(.02,-.17,.012)],s=>.0024,{seed:R(),sides:3});
  this.attach('wrist'+sd,B,this.ink);this.attach('wrist'+sd,C,this.crimson);
  this.fingers=this.fingers||{};this.fingers[sd]=[];
  const spread=[-.045,-.015,.015,.045],lens=[[.2,.16,.14],[.23,.18,.16],[.22,.17,.15],[.18,.15,.13]];
  for(let f=0;f<5;f++){const thumb=f===4;let parent=w;const base=thumb?V(s*-.04,-.08,.02):V(spread[f]*(s<0?-1:1),-.22,0);const chain=[];
   const L=thumb?[.12,.1,.09]:lens[f];
   for(let j=0;j<3;j++){const g=new T.Group();g.position.copy(j===0?base:V(0,-L[j-1],0));parent.add(g);parent=g;chain.push(g);
    const FB=new TubeBuilder();const len=L[j];
    for(let k=0;k<4;k++){const o=V((R()-.5)*.008,0,(R()-.5)*.008);const pts=[V(0,.012,0).add(o),V(0,-len*.5,0).add(o.clone().multiplyScalar(1.4)),V(0,-len-.006,0).add(o)];FB.tube(pts,s=>.0095*(1-.35*s)*(j===2?(1-s*.85):1),{sides:5,shade:R()});}
    if(j===2){FB.tube([V(0,-len+.01,0),V(0,-len-.05,.015),V(0,-len-.1,.045)],s=>.006*(1-s),{sides:5});}
    if(R()<.5)branch(FB,R,V(0,-len*.5,0),V((R()-.5),-.5,(R()-.5)).normalize(),.05+R()*.06,.0018,1,{sway0:.2,swayPerM:3,kids:2,thorns:0});
    const m=new T.Mesh(FB.geometry(),this.ink);m.frustumCulled=false;m.castShadow=true;m.customDepthMaterial=this.depth;g.add(m);this.meshes.push(m);}
   this.fingers[sd].push(chain);}
 }
 cloth(){
  const R=this.R;this.clothMat=[];
  const mk=(seed,grey)=>{const m=patchGrowth(new T.MeshBasicMaterial({map:clothTexture(seed),color:new T.Color(grey,grey,grey),transparent:true,opacity:.45,side:T.DoubleSide,depthWrite:false,fog:true,alphaTest:.02}),this.uniforms,'');return m;};
  const mats=[mk(11,.6),mk(23,.45),mk(37,.72)];
  // torn strips hang from the waist and lower ribs and wrap the thighs like the reference's ragged shroud
  for(let k=0;k<8;k++){const th=-Math.PI*.9+k/7*Math.PI*1.8+(R()-.5)*.3;const r=.12+R()*.05;const top=k%4===0?.3:.02;const len=.7+R()*.8,w=.16+R()*.16;
   const g=new T.PlaneGeometry(w,len,3,14);g.translate(0,-len/2,0);
   const p=g.attributes.position;for(let i=0;i<p.count;i++){const y=p.getY(i),x=p.getX(i);p.setZ(i,Math.sin(x*25+y*6+k)*.02+(-y)*.08);}
   growthAttrs(g,(x,y)=>clamp(-y*1.4)*1.3);
   const m=new T.Mesh(g,mats[k%3]);m.position.set(Math.sin(th)*r,top,Math.cos(th)*r*.8);m.rotation.y=th;m.renderOrder=2;m.frustumCulled=false;this.bones[top>.1?'spine':'pelvis'].add(m);}
 }
 fingerRest(){}
 // Pose is a pure function of time.
 pose(t,k){
  const b=this.bones;this.uniforms.uTime.value=t;
  const br=Math.sin(t*1.05)*.5+Math.sin(t*.43)*.5; // slow, uneven breathing
  // torso stoops over the bed; leans further in during the descent
  const lean=k.lean;b.pelvis.rotation.set(.05,0,0);b.spine.rotation.set(.26+lean*.3+br*.012,0,.04+Math.sin(t*.31)*.01);
  b.neck.rotation.set(.62+lean*.25,0,0);
  // head: authored tilt (7 deg) and a slow turn toward the sleeper
  b.head.rotation.set(.55+k.headDown+Math.sin(t*.7)*.006,k.headTurn,k.headTilt);
  // reaching (right) arm
  const r=k.reach;b.shoulderR.rotation.set(-.2-lean*.3-r*1.18+br*.01,0,-.1-r*.1);b.elbowR.rotation.set(-.1+r*.28+Math.sin(t*.9)*.015,0,.05);b.wristR.rotation.set(.15+r*.3,0,-.08);
  // left arm hangs long, fingers drifting
  b.shoulderL.rotation.set(-.24-lean*.3+Math.sin(t*.5)*.03,0,.16);b.elbowL.rotation.set(-.12+Math.sin(t*.37+1)*.03,0,-.04);b.wristL.rotation.set(.18,0,.06);
  // fingers: unfold as the hand opens, then slowly curl toward the face
  for(const sd of ['L','R']){const open=sd==='R'?k.open:.2+.08*Math.sin(t*.6);this.fingers[sd].forEach((chain,f)=>{const ph=f*.7+(sd==='R'?0:2);
   chain.forEach((g,j)=>{const curl=(1-open)*(j===0?.5:.75)+k.claw*(j===0?.15:.35)+Math.sin(t*1.3+ph+j)*.025;g.rotation.set(-curl*(f===4?.6:1),0,(f===4?(sd==='R'?-.6:.6):(f-1.5)*.08*open));});});}
  b.hipL.rotation.set(-.08,0,.02);b.hipR.rotation.set(-.04,0,-.02);b.kneeL.rotation.set(.06,0,0);b.kneeR.rotation.set(.05,0,0);
 }
 jointScales(){return Object.values(this.bones).map(g=>g.scale.toArray());}
}
