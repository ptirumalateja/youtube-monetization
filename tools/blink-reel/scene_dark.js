// You Were Blind for 20 Minutes Today, Slow Light Dark look (V2, 28 Oct 2026): the void, one gold lamp beam with dust, a soft-mirror floor and
// the cream free-flowing stickman (sld.js). Each moment of his day is staged in the same pool of light. Screen-space eyelids (grade uLid)
// close on every blink; his two eye dots close with them, except in the mirror. Then an eye macro and a neural field.
// renderAt(t) is pure. Units are metres. Pool at the origin, eye at x=60, neural field at x=120.
import * as THREE from 'three';
import {Reflector} from 'three/addons/objects/Reflector.js';
import * as SLD from './sld.js';
import * as SETS from './sets.js';
import {buildEye} from './eye.js';
const {V,clamp,sstep,lerp,sm5,PAL}=SLD;
const {M,B,C,S:SPH,P:PLN,canvasTex,rng}=SETS;
const q=new URLSearchParams(location.search); const W=+q.get('w')||540, H=+q.get('h')||960;
const DUR=22.0;
const ST=SLD.createStage({W,H}); const scene=ST.scene; const R=SLD.createRig(scene);

// ---------------------------------------------------------------- blinks (screen lids) and the shot list
// V3 (payoff-first): the eye blinks in the hook; screen lids carry the day; the brain cuts out on each blink; the mirror dare; the CTA; lids close into the loop.
const BLINKS=[3.3,4.75, 5.9,6.85,7.8,8.65, 9.05,9.3,9.5,9.66,9.8,9.9, 12.4, 18.6,19.75];
const EYEBLINKS=[-0.12,1.2, 13.45];           // real-lid blinks in the eye shots (the first one is already shut at frame 0)
const BRAINBLINKS=[15.5,16.35];
const lidOne=(t,b)=>{ const u=t-b; if(u<0||u>0.22) return 0; if(u<0.06) return sm5(u/0.06); if(u<0.13) return 1; return 1-sm5((u-0.13)/0.09); };
function lidAt(t){ let l=0; if(t<0.14) l=1-sm5(clamp((t-0.03)/0.11)); if(t>21.82) l=Math.max(l,sm5(clamp((t-21.82)/0.08))); for(const b of BLINKS) l=Math.max(l,lidOne(t,b)); return l; }
const SHOTS=[
  {id:'eyehook',t0:0.0, t1:2.4},
  {id:'read',   t0:2.4, t1:3.9,  tod:'night'},
  {id:'read2',  t0:3.9, t1:5.4,  tod:'night'},
  {id:'window', t0:5.4, t1:6.4,  tod:'morning'},
  {id:'desk',   t0:6.4, t1:7.4,  tod:'noon'},
  {id:'bed',    t0:7.4, t1:8.4,  tod:'evening'},
  {id:'readn',  t0:8.4, t1:9.3,  tod:'night'},
  {id:'wide',   t0:9.3, t1:11.2, tod:'night'},
  {id:'life',   t0:11.2,t1:13.0, tod:'night'},
  {id:'eye',    t0:13.0,t1:14.6},
  {id:'brain',  t0:14.6,t1:17.0},
  {id:'mirror', t0:17.0,t1:22.0, tod:'night'} ];
const shotAt=t=>SHOTS.find(s=>t>=s.t0&&t<s.t1)||SHOTS[SHOTS.length-1];

// ---------------------------------------------------------------- what he looks at (seen in the POV shots): page text, sunrise, laptop doc, phone feed
const WORDS='the light had gone out of the room before she noticed it and the long hour after was only the slow return of things she had stopped seeing because she had stopped looking and the window held the last of the evening like water in a glass'.split(' ');
const pageTex=sd=>canvasTex(512,768,(g,w,h)=>{ const r=rng(sd); g.fillStyle='#efe6d4'; g.fillRect(0,0,w,h); const gr=g.createLinearGradient(sd%2?w:0,0,sd%2?0:w,0); gr.addColorStop(0,'rgba(90,70,40,0.35)'); gr.addColorStop(0.12,'rgba(90,70,40,0)'); g.fillStyle=gr; g.fillRect(0,0,w,h);
  g.fillStyle='#2a2420'; g.font='19px Georgia, serif'; let y=70; while(y<h-50){ let x=44, line=''; while(true){ const wd=WORDS[Math.floor(r()*WORDS.length)]; if(g.measureText(line+wd+' ').width>w-88) break; line+=wd+' '; } g.fillText(line,x,y); y+=30; }
  g.font='15px Georgia, serif'; g.fillText(String(140+sd),w/2-12,h-24); });
const skyTex=canvasTex(1024,1280,(g,w,h)=>{ const r=rng(41); const gr=g.createLinearGradient(0,0,0,h); gr.addColorStop(0,'#7fa6d8'); gr.addColorStop(0.55,'#d8c8c4'); gr.addColorStop(0.75,'#ffd9a8'); gr.addColorStop(1,'#ffe8c8'); g.fillStyle=gr; g.fillRect(0,0,w,h);
  const sg=g.createRadialGradient(w*0.66,h*0.7,10,w*0.66,h*0.7,360); sg.addColorStop(0,'rgba(255,250,230,1)'); sg.addColorStop(0.15,'rgba(255,236,190,0.9)'); sg.addColorStop(1,'rgba(255,220,170,0)'); g.fillStyle=sg; g.fillRect(0,0,w,h);
  for(const [base,hm,col] of [[h*0.86,h*0.12,'rgba(150,150,175,0.55)'],[h*0.92,h*0.2,'rgba(95,95,120,0.8)'],[h,h*0.3,'#3a3a4a']]){ let x=-10; g.fillStyle=col; while(x<w){ const bw=40+r()*90, bh=hm*(0.3+0.7*r()); g.fillRect(x,base-bh,bw,h); x+=bw+3; } }
  g.strokeStyle='rgba(40,40,50,0.6)'; g.lineWidth=2; for(let i=0;i<4;i++){ const bx=200+r()*500, by=200+r()*300; g.beginPath(); g.moveTo(bx-9,by); g.quadraticCurveTo(bx-4,by-6,bx,by); g.quadraticCurveTo(bx+4,by-6,bx+9,by); g.stroke(); } });
const lapTex=canvasTex(768,480,(g,w,h)=>{ const r=rng(43); g.fillStyle='#1d2330'; g.fillRect(0,0,w,h); g.fillStyle='#2a3242'; g.fillRect(0,0,w,34); g.fillStyle='#f4f1ea'; g.fillRect(150,52,w-300,h-52);
  g.fillStyle='#1d1d22'; g.font='bold 22px Helvetica, Arial'; g.fillText('Q3 notes',176,92); g.font='14px Helvetica, Arial'; for(let y=124;y<h-20;y+=22){ g.fillStyle='rgba(40,40,48,0.85)'; g.fillRect(176,y,(w-352)*(0.55+0.45*r()),7); } g.fillStyle='#4a7fd0'; g.fillRect(176+(w-352)*0.3,124+22*7,2,16);
  for(const [x,c] of [[18,'#ff5f57'],[38,'#febc2e'],[58,'#28c840']]){ g.fillStyle=c; g.beginPath(); g.arc(x,17,6,0,7); g.fill(); } });
const phoneTex=canvasTex(360,760,(g,w,h)=>{ const r=rng(47); g.fillStyle='#0e0f14'; g.fillRect(0,0,w,h); let y=40; for(let k=0;k<4;k++){ const hue=[18,200,330,45][k];
    g.fillStyle=`hsl(${hue},55%,${45+10*r()}%)`; g.fillRect(14,y+40,w-28,170); const gr=g.createLinearGradient(0,y+40,0,y+210); gr.addColorStop(0,'rgba(255,255,255,0.15)'); gr.addColorStop(1,'rgba(0,0,0,0.35)'); g.fillStyle=gr; g.fillRect(14,y+40,w-28,170);
    g.fillStyle='#ddd'; g.beginPath(); g.arc(30,y+18,12,0,7); g.fill(); g.fillStyle='rgba(230,230,235,0.8)'; g.fillRect(50,y+12,120,8); g.fillStyle='rgba(230,230,235,0.5)'; g.fillRect(14,y+222,w*0.7,7); y+=260; } });
// ---------------------------------------------------------------- the props, each staged in the pool of light (dark materials, faint rim)
const IRONM=M(0x3a3b40,{r:0.55,m:0.3}), DARKW=M(0x2a2420,{r:0.7}), FAB=M(0x4a3a36,{r:0.95});
const G={}; const mk=id=>{ const g=new THREE.Group(); g.visible=false; scene.add(g); G[id]=g; return g; };
{ const ch=mk('chair'); B(ch,0.78,0.42,0.74,FAB,0,0.21,0,{round:0.08}); B(ch,0.78,0.62,0.18,FAB,-0.02,0.64,-0.3,{round:0.08}); for(const sx of [-1,1]) B(ch,0.16,0.3,0.74,FAB,sx*0.39,0.52,0,{round:0.06}); ch.position.set(0.05,0,-0.05); ch.rotation.y=0.3; }
const paneM=new THREE.MeshBasicMaterial({map:skyTex,color:0x8c8c8c,fog:false});
{ const w=mk('window'); B(w,1.3,1.6,0.06,DARKW,0,0,0); PLN(w,1.18,1.48,paneM,0,0,0.035); B(w,0.035,1.6,0.07,DARKW,0,0,0.04); B(w,1.3,0.035,0.07,DARKW,0,0,0.04); w.position.set(0,1.55,-1.45); }
const winLight=new THREE.SpotLight(0xcfe0ff,0,8,0.7,0.6,1.2); winLight.position.set(0,1.6,-1.8); winLight.target.position.set(0,0.9,1.5); scene.add(winLight,winLight.target);
const screenM=new THREE.MeshBasicMaterial({map:lapTex,color:0x9a9a9a,fog:false});
{ const dk=mk('desk'); B(dk,1.2,0.05,0.6,DARKW,0,0.76,0,{round:0.01}); for(const [x,z] of [[-0.55,-0.25],[0.55,-0.25],[-0.55,0.25],[0.55,0.25]]) B(dk,0.04,0.76,0.04,IRONM,x,0.38,z);
  const lt=new THREE.Group(); B(lt,0.36,0.015,0.25,M(0x8a8c92,{m:0.6,r:0.35}),0,0,0); const lid=new THREE.Group(); B(lid,0.36,0.24,0.012,M(0x8a8c92,{m:0.6,r:0.35}),0,0.12,0); PLN(lid,0.33,0.21,screenM,0,0.12,0.007); lid.position.set(0,0.008,-0.12); lid.rotation.x=-0.25; lt.add(lid); lt.position.set(0,0.79,-0.02); dk.add(lt);   // screen faces the chair
  C(dk,0.045,0.04,0.1,M(0xd9c8a8,{r:0.4}),0.42,0.83,0.05); B(dk,0.46,0.05,0.44,DARKW,0,0.47,0.62); B(dk,0.46,0.5,0.05,DARKW,0,0.75,0.84); for(const [x,z] of [[-0.2,0.43],[0.2,0.43],[-0.2,0.81],[0.2,0.81]]) B(dk,0.04,0.47,0.04,IRONM,x,0.235,z);
  dk.position.set(0,0,-0.45); }
const lapLight=new THREE.PointLight(0xbcd4ff,0,2.2,2); scene.add(lapLight);
{ const bd=mk('bed'); B(bd,2.0,0.3,1.3,DARKW,0,0.15,0,{round:0.03}); B(bd,1.9,0.2,1.2,M(0xd8d2c6,{r:0.9}),0,0.4,0,{round:0.07}); B(bd,1.2,0.12,1.24,M(0x3a4258,{r:0.95}),0.35,0.54,0,{round:0.06}); B(bd,0.4,0.15,0.8,M(0xe8e2d6,{r:0.95}),-0.75,0.56,0,{round:0.07}); bd.position.set(0.05,0,-0.35); }
const MIR={w:0.62,h:1.5}; const mirG=mk('mirror'); B(mirG,MIR.w+0.1,MIR.h+0.1,0.05,M(0x8a6a3a,{m:0.6,r:0.35}),0,0,-0.03); for(const sx of [-1,1]) B(mirG,0.04,0.5,0.04,IRONM,sx*0.25,-0.95,-0.15,{rx:0.4});
const mirror=new Reflector(new THREE.PlaneGeometry(MIR.w,MIR.h),{textureWidth:Math.round(W*0.7),textureHeight:Math.round(W*0.7*MIR.h/MIR.w),color:0xb8b4ac,clipBias:0.003}); mirG.add(mirror); mirG.position.set(0,1.05,-1.55);
// distant furniture silhouettes at the edge of the light, so the void has depth (shelf, lamp stand, plant)
{ const bg=mk('bg'); bg.visible=true; B(bg,1.1,1.9,0.35,M(0x1c1c20,{r:0.9}),-2.6,0.95,-3.2); B(bg,0.9,0.04,0.25,M(0x26262a),2.4,1.6,-3.4); B(bg,0.9,0.04,0.25,M(0x26262a),2.4,1.1,-3.4); C(bg,0.12,0.09,0.22,M(0x2a2420),2.9,0.11,-2.6); }

// ---------------------------------------------------------------- small props: book, mug, phone
const rbook=new THREE.Group(); { const pg=M(0xf4efe6,{r:0.9}), cv=M(0x5a4a3a,{r:0.7}); for(const sx of [-1,1]){ const h=new THREE.Group(); B(h,0.13,0.012,0.19,cv,sx*0.065,0,0); B(h,0.12,0.02,0.18,pg,sx*0.062,0.012,0); PLN(h,0.116,0.176,new THREE.MeshStandardMaterial({map:pageTex(sx>0?2:1),color:0x5a544c,roughness:0.95}),sx*0.062,0.0225,0,{rx:-Math.PI/2}); h.rotation.z=-sx*0.28; rbook.add(h); } } scene.add(rbook);
const mug=new THREE.Group(); C(mug,0.045,0.04,0.1,M(0xe8e1d4,{r:0.4}),0,0,0); scene.add(mug);
const phone=new THREE.Group(); { B(phone,0.075,0.15,0.01,M(0x0d0e12,{r:0.3,m:0.4}),0,0,0,{round:0.01}); B(phone,0.067,0.138,0.004,new THREE.MeshBasicMaterial({map:phoneTex,color:0x8a8a8a}),0,0,0.006,{cast:false}); } phone.scale.setScalar(1.4); scene.add(phone); const phoneLight=new THREE.PointLight(0xbcd4ff,0,2.2,2); scene.add(phoneLight);

// ---------------------------------------------------------------- the hero: cream free-flowing stickman with two eye dots
const hero=R.makeFig(PAL.CREAM,'hero',{rim:0.16,lift:0.07});
const eyeDotM=new THREE.MeshStandardMaterial({color:0x14151a,roughness:0.4}); const eyes=[0,1].map(()=>{ const e=new THREE.Mesh(new THREE.SphereGeometry(1,16,12),eyeDotM); e.frustumCulled=false; scene.add(e); return e; });
function placeEyes(J,shut){ const hd=J.head, up=J.head.clone().sub(J.neck).normalize(); let f=J.fwd.clone().addScaledVector(up,-J.fwd.dot(up)).normalize(); const sd=f.clone().cross(up).normalize();
  eyes.forEach((e,i)=>{ e.position.copy(hd).addScaledVector(f,0.118).addScaledVector(sd,(i?1:-1)*0.046).addScaledVector(up,0.018); e.scale.set(0.017,0.024*(shut?0.12:1),0.012); e.quaternion.setFromRotationMatrix(new THREE.Matrix4().makeBasis(sd,up,f)); e.visible=true; }); }
const EYE=new THREE.Group(); EYE.position.set(60,0,0); scene.add(EYE);
const irisTex=canvasTex(2048,1024,(g,w,h)=>{ // equirect with the iris around the top pole (v=0); the ball is turned so that pole faces the camera
  g.fillStyle='#eadfd2'; g.fillRect(0,0,w,h); const Rr=rng(8); g.strokeStyle='rgba(170,50,45,0.28)'; g.lineWidth=2; for(let i=0;i<90;i++){ let x=Rr()*w, y=h*(0.3+Rr()*0.45); g.beginPath(); g.moveTo(x,y); for(let k=0;k<7;k++){ x+=(Rr()-0.5)*50; y-=Rr()*28; g.lineTo(x,y); } g.stroke(); }
  const rows=r=>r/Math.PI*h; const iR=rows(0.56), pR=rows(0.2), lR=rows(0.6);
  const gr=g.createLinearGradient(0,0,0,lR); gr.addColorStop(0,'#050403'); gr.addColorStop(pR/lR*0.98,'#050403'); gr.addColorStop(pR/lR*1.02,'#5a3412'); gr.addColorStop(0.55,'#b07a30'); gr.addColorStop(0.8,'#6a4218'); gr.addColorStop(iR/lR,'#24140a'); gr.addColorStop(1,'rgba(234,223,210,1)'); g.fillStyle=gr; g.fillRect(0,0,w,lR);
  for(let i=0;i<2600;i++){ const x=Rr()*w; g.strokeStyle=`rgba(${Rr()<0.55?'245,200,120':'30,16,8'},${0.08+Rr()*0.22})`; g.lineWidth=1+Rr()*4; g.beginPath(); g.moveTo(x,pR+2+Rr()*6); g.lineTo(x+(Rr()-0.5)*14,pR+(iR-pR)*(0.5+Rr()*0.5)); g.stroke(); }
  g.fillStyle='#050403'; g.fillRect(0,0,w,pR); });
const eyeM=new THREE.MeshPhysicalMaterial({map:irisTex,roughness:0.3,clearcoat:1,clearcoatRoughness:0.04});
const eyeBall=new THREE.Mesh(new THREE.SphereGeometry(1,128,96),eyeM); eyeBall.rotation.x=Math.PI/2; const eyeRig=new THREE.Group(); eyeRig.add(eyeBall);
const cornea=new THREE.Mesh(new THREE.SphereGeometry(0.62,64,32),new THREE.MeshPhysicalMaterial({color:0xffffff,roughness:0.0,transparent:true,opacity:0.12,clearcoat:1,clearcoatRoughness:0})); cornea.position.z=0.47; eyeRig.add(cornea);
const skinM=new THREE.MeshStandardMaterial({color:0x9a6a52,roughness:0.6}); const lidG=new THREE.SphereGeometry(1.06,96,48,0,Math.PI*2,0,Math.PI/2);
const lidTop=new THREE.Group(), lidBot=new THREE.Group(); { const a=new THREE.Mesh(lidG,skinM); lidTop.add(a); const b=new THREE.Mesh(lidG,skinM); b.rotation.x=Math.PI; lidBot.add(b); }
// lash line
{ const lm=new THREE.MeshStandardMaterial({color:0x1a0d08,roughness:0.8}); const lt=new THREE.Mesh(new THREE.TorusGeometry(1.06,0.03,8,96,Math.PI),lm); lt.rotation.x=Math.PI/2; lidTop.add(lt); const lb=lt.clone(); lb.rotation.set(Math.PI/2,0,0); lidBot.add(lb); }
// V2.1: the old stylised eye stays built (shared helpers) but is replaced on screen by eye.js

const face=new THREE.Mesh(new THREE.TorusGeometry(1.45,0.5,32,128),skinM); face.scale.set(1.35,0.95,0.7); face.position.z=0.1; const brow=new THREE.Mesh(new THREE.SphereGeometry(1.4,48,24),skinM); brow.scale.set(1.9,0.55,0.9); brow.position.set(0,1.55,0.05);
const eyeLight=new THREE.PointLight(0xffc890,0,9,1.5); scene.add(eyeLight);
function eyeLids(open){ // open 1 = wide (lids rotated off the cornea), 0 = shut
  lidTop.rotation.x=-lerp(0.0,0.82,open); lidBot.rotation.x=lerp(0.0,0.62,open); }

// ---------------------------------------------------------------- the neural field (visual cortex)
const BRAIN=new THREE.Group(); BRAIN.position.set(120,0,0); scene.add(BRAIN);
const brainU={uT:{value:0},uB:{value:1},uH:{value:H}};
{ const N=90000, Rr=rng(31), pos=new Float32Array(N*3), sd=new Float32Array(N), col=new Float32Array(N*3);
  for(let i=0;i<N;i++){ const z=-Rr()*26, x=(Rr()-0.5)*7, y0=(Rr()-0.5)*9; const fold=0.55*Math.sin(x*1.7+z*0.35)+0.35*Math.sin(y0*1.3-z*0.5); const layer=Math.floor(Rr()*3)-1;
    pos[i*3]=x+0.2*Math.sin(z); pos[i*3+1]=y0+fold+layer*0.6; pos[i*3+2]=z+fold*0.5; sd[i]=Rr(); const g=Rr()<0.78; col[i*3]=g?1.0:0.36; col[i*3+1]=g?0.72:0.78; col[i*3+2]=g?0.38:0.75; }
  const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.BufferAttribute(pos,3)); geo.setAttribute('seed',new THREE.BufferAttribute(sd,1)); geo.setAttribute('col',new THREE.BufferAttribute(col,3));
  const m=new THREE.Points(geo,new THREE.ShaderMaterial({uniforms:brainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute float seed; attribute vec3 col; uniform float uT,uH,uB; varying vec3 vC; varying float vA;
      void main(){ vec3 p=position; float s=seed*6.283; p.x+=0.05*sin(uT*0.8+s); p.y+=0.05*cos(uT*0.6+s*1.3);
        float fire=pow(0.5+0.5*sin(uT*(1.5+seed*4.0)+s*3.0),6.0);
        vec4 mv=modelViewMatrix*vec4(p,1.0); gl_Position=projectionMatrix*mv; float sz=(0.028+0.045*fire)*uH/(-mv.z);
        gl_PointSize=clamp(sz,1.0,30.0); vC=col; vA=(0.25+0.9*fire)*uB*clamp(1.0-(-mv.z)/24.0,0.0,1.0)*min(1.0,sz/1.5); }`,
    fragmentShader:`varying vec3 vC; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vC*a*a*vA*1.1,1.0); }`}));
  m.frustumCulled=false; BRAIN.add(m);
  // neurons: short glowing threads between nearby cells, a pulse runs along each
  const NL=14000, lp=new Float32Array(NL*6), la=new Float32Array(NL*2), ls=new Float32Array(NL*2);
  for(let i=0;i<NL;i++){ const a=Math.floor(Rr()*N); const ax=pos[a*3],ay=pos[a*3+1],az=pos[a*3+2]; const d=0.25+Rr()*0.6, th=Rr()*6.283, ph=(Rr()-0.5)*1.2;
    lp.set([ax,ay,az, ax+Math.cos(th)*Math.cos(ph)*d, ay+Math.sin(ph)*d, az+Math.sin(th)*Math.cos(ph)*d],i*6); la[i*2]=0; la[i*2+1]=1; ls[i*2]=ls[i*2+1]=Rr(); }
  const lg=new THREE.BufferGeometry(); lg.setAttribute('position',new THREE.BufferAttribute(lp,3)); lg.setAttribute('along',new THREE.BufferAttribute(la,1)); lg.setAttribute('seed',new THREE.BufferAttribute(ls,1));
  const lm=new THREE.LineSegments(lg,new THREE.ShaderMaterial({uniforms:brainU,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute float along; attribute float seed; uniform float uT; varying float vL; varying float vS; varying float vD; void main(){ vL=along; vS=seed; vec4 mv=modelViewMatrix*vec4(position,1.0); vD=-mv.z; gl_Position=projectionMatrix*mv; }`,
    fragmentShader:`uniform float uT,uB; varying float vL; varying float vS; varying float vD; void main(){ float p=fract(uT*0.9+vS*7.0); float pulse=exp(-pow((vL-p)*7.0,2.0)); float fade=clamp(1.0-vD/20.0,0.0,1.0); gl_FragColor=vec4(vec3(1.0,0.74,0.4)*(0.05+0.6*pulse)*uB*fade,1.0); }`}));
  lm.frustumCulled=false; BRAIN.add(lm); }const eyeSpot=new THREE.SpotLight(0xffc890,0,14,0.5,0.7,1.2); eyeSpot.position.set(57.6,3.0,5.0); eyeSpot.target.position.set(60,0,0); scene.add(eyeSpot,eyeSpot.target);
const EYEM=buildEye(ST.renderer); EYE.add(EYEM.group);

// ---------------------------------------------------------------- V3 brain: a glowing brain you can recognise (two hemispheres with gyri, cerebellum, stem).
// The visual cortex at the back burns gold, fed by pulses running back from the eyes along the optic radiation; on a blink it all cuts out.
const BRAIN2=new THREE.Group(); BRAIN2.position.set(180,0,0); scene.add(BRAIN2);
const b2U={uT:{value:0},uB:{value:1},uOcc:{value:1},uH:{value:H}};
{ const Rr=rng(77), P=[], A=[]; // A: [kind, occipital weight, seed]
  const gyri=(x,y,z)=>Math.sin(9.0*(y+0.28*Math.sin(3.1*z+1.3*x))+3.2*Math.sin(4.3*z-2.0*y)+2.0*Math.sin(5.5*x+z)+1.4*Math.sin(6.0*x*z+5.0*y+2.0*z*z));
  for(let i=0;i<150000;i++){ const side=Rr()<0.5?-1:1; let th=Math.acos(2*Rr()-1), ph=Rr()*Math.PI*2; let dx=Math.sin(th)*Math.cos(ph), dy=Math.cos(th), dz=Math.sin(th)*Math.sin(ph);
    if(dx*side<-0.55) continue; // medial wall mostly hidden
    let x=side*0.33+dx*0.42, y=dy*0.6, z=dz*0.86; if(y<0) y*=0.75+0.25*Math.exp(-((z-0.25)**2)/0.12); // flatter base, temporal lobe drop
    if(y<-0.3&&z<-0.35) continue;
    const g=gyri(x,y,z); if(Math.abs(g)<0.22) continue; const r=1+0.035*g; x=side*0.33+(x-side*0.33)*r; y*=r; z*=r;
    const occ=sstep(-0.35,-0.7,z)*sstep(-0.45,0.1,y)*(0.85+0.15*Math.sin(17*x+11*y)); P.push(x,y,z); A.push(0,occ,Rr()); }
  for(let i=0;i<26000;i++){ let th=Math.acos(2*Rr()-1), ph=Rr()*Math.PI*2; const x=Math.sin(th)*Math.cos(ph)*0.5, y=-0.5+Math.cos(th)*0.22, z=-0.62+Math.sin(th)*Math.sin(ph)*0.3; if(Math.abs(Math.sin(y*90))<0.3) continue; P.push(x,y,z); A.push(1,0.2,Rr()); }
  for(let i=0;i<5000;i++){ const u=Rr(), a=Rr()*6.283; P.push(Math.cos(a)*0.09,-0.35-u*0.55,-0.32+Math.sin(a)*0.09-u*0.08); A.push(2,0,Rr()); }
  const g=new THREE.BufferGeometry(); g.setAttribute('position',new THREE.Float32BufferAttribute(P,3)); g.setAttribute('info',new THREE.Float32BufferAttribute(A,3));
  const m=new THREE.Points(g,new THREE.ShaderMaterial({uniforms:b2U,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute vec3 info; uniform float uT,uH,uB,uOcc; varying vec3 vC; varying float vA;
      void main(){ vec4 mv=modelViewMatrix*vec4(position,1.0); gl_Position=projectionMatrix*mv; float s=info.z*6.283;
        float fire=pow(0.5+0.5*sin(uT*(2.0+info.z*5.0)+s*3.0),5.0); float occ=info.y*uOcc;
        vec3 cool=vec3(0.42,0.5,0.66), gold=vec3(1.0,0.7,0.34); vC=mix(cool,gold,clamp(occ*1.2,0.0,1.0)); if(info.x>1.5) vC=vec3(0.35,0.4,0.52);
        float sz=(0.011+0.012*fire*(0.3+occ))*uH/(-mv.z); gl_PointSize=clamp(sz,1.0,14.0);
        vA=(0.1+0.32*fire*occ+0.3*occ)*uB*min(1.0,sz/1.2); }`,
    fragmentShader:`varying vec3 vC; varying float vA; void main(){ float d=length(gl_PointCoord-0.5); float a=smoothstep(0.5,0.0,d); gl_FragColor=vec4(vC*a*vA,1.0); }`}));
  m.frustumCulled=false; BRAIN2.add(m);
  const NT=70, SEG=40, lp=[], la=[], ls=[];
  for(let k=0;k<NT;k++){ const side=k%2?1:-1, sd=Rr(); const p0=new THREE.Vector3(side*0.08,-0.28,0.62), p1=new THREE.Vector3(side*(0.28+0.12*Rr()),-0.1+0.12*Rr(),0.0), p2=new THREE.Vector3(side*(0.18+0.12*Rr()),-0.05+0.2*Rr(),-0.76);
    const c=new THREE.QuadraticBezierCurve3(p0,p1,p2); const pts=c.getPoints(SEG); for(let j=0;j<SEG;j++){ lp.push(...pts[j].toArray(),...pts[j+1].toArray()); la.push(j/SEG,(j+1)/SEG); ls.push(sd,sd); } }
  const lg=new THREE.BufferGeometry(); lg.setAttribute('position',new THREE.Float32BufferAttribute(lp,3)); lg.setAttribute('along',new THREE.Float32BufferAttribute(la,1)); lg.setAttribute('seed',new THREE.Float32BufferAttribute(ls,1));
  const lm=new THREE.LineSegments(lg,new THREE.ShaderMaterial({uniforms:b2U,transparent:true,depthWrite:false,blending:THREE.AdditiveBlending,fog:false,
    vertexShader:`attribute float along; attribute float seed; varying float vL; varying float vS; void main(){ vL=along; vS=seed; gl_Position=projectionMatrix*modelViewMatrix*vec4(position,1.0); }`,
    fragmentShader:`uniform float uT,uB,uOcc; varying float vL; varying float vS; void main(){ float p=fract(uT*1.3+vS*5.0); float pulse=exp(-pow((vL-p)*9.0,2.0)); gl_FragColor=vec4(vec3(1.0,0.76,0.42)*(0.04+0.9*pulse)*uB*uOcc,1.0); }`}));
  lm.frustumCulled=false; BRAIN2.add(lm); }

// ---------------------------------------------------------------- hero poses, all inside the pool of light
const sitP=(o={})=>({...R.P0,aL:1.5,aR:1.5,kL:1.5,kR:1.5,...o});
const breathe=t=>0.014*Math.sin(2*Math.PI*0.23*t);
function heroPose(t,id){ const ex={}; let J,P,root,yaw;
  if(id==='read'||id==='read2'||id==='readn'||id==='wide'||id==='life'){ root=V(0.0,0,0.05); yaw=SLD.yawOf(V(0.3,0,0.95)); P=sitP({p:0.14+breathe(t),tilt:0.42+0.03*Math.sin(t*0.9),hy:0.06*Math.sin(t*0.5),eL:1.0,eR:1.0});
    const J0=R.skel(P,root,yaw); const f=J0.fwd, sd=V(-f.z,0,f.x); const bc=J0.neck.clone().addScaledVector(f,0.33).add(V(0,-0.2,0));
    if(t>4.2&&t<4.65){ bc.addScaledVector(sd,0.04*Math.sin(Math.PI*(t-4.2)/0.45)); }    // page turn
    P.tL=bc.clone().addScaledVector(sd,0.1); P.wL=1; P.pL=V(-0.3,-0.7,0.6); P.tR=bc.clone().addScaledVector(sd,-0.1); P.wR=1; P.pR=V(-0.3,-0.7,-0.6); J=R.skel(P,root,yaw); ex.book={pos:bc,f}; }
  else if(id==='window'){ root=V(0,0,-0.7); yaw=SLD.yawOf(V(0.05,0,-1)); P={...R.P0,p:0.03+breathe(t),tilt:-0.12}; const J0=R.skel(P,root,yaw);
    const sip=sstep(5.7,6.0,t)*(1-sstep(6.15,6.35,t)); const mp=J0.neck.clone().addScaledVector(J0.fwd,0.24).add(V(0,-0.24+0.13*sip,0)).addScaledVector(V(-J0.fwd.z,0,J0.fwd.x),-0.13);
    P.tR=mp; P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); ex.mug=J.hR.clone(); }
  else if(id==='desk'){ root=V(0,0,0.17); yaw=SLD.yawOf(V(0,0,-1)); P=sitP({p:0.3+breathe(t),tilt:0.25,eL:1.0,eR:1.0}); const ty=t*13;
    P.tL=V(-0.1,0.83+Math.max(0,Math.sin(ty))*0.014,-0.36); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=V(0.12,0.83+Math.max(0,Math.sin(ty+2))*0.014,-0.36); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); }
  else if(id==='bed'){ root=V(0.1,0,0.42); yaw=SLD.yawOf(V(0.2,0,1)); P=sitP({p:0.42+breathe(t),tilt:0.55,eL:1.2,eR:1.2,dy:0.05}); const J0=R.skel(P,root,yaw); const pp=J0.neck.clone().addScaledVector(J0.fwd,0.28).add(V(0,-0.28,0));
    P.tL=pp.clone(); P.wL=1; P.pL=V(-0.3,-0.7,0.5); P.tR=pp.clone().add(V(0,0.02,0)); P.wR=1; P.pR=V(-0.3,-0.7,-0.5); J=R.skel(P,root,yaw); ex.phone={pos:pp.clone().add(V(0,0.04,0)),f:J.fwd}; }
  else { root=V(0,0,-0.8); yaw=SLD.yawOf(V(0.03,0,-1)); const lean=sstep(17.2,18.4,t); P={...R.P0,p:0.04+0.07*lean+breathe(t),tilt:0.0,hy:0.08*Math.sin(t*0.7)}; J=R.skel(P,root,yaw); }
  return {J,ex}; }

// ---------------------------------------------------------------- light per time of day (the lamp changes colour; window / screen / phone add their own)
const TOD={ night:{col:PAL.GOLD,k:1.0}, morning:{col:0xd8e4f6,k:0.55}, noon:{col:0xfff0d8,k:0.55}, evening:{col:0xff9a52,k:0.9} };
const CAMS={
  read:[[0.9,1.3,5.6],[0,0.85,0],[0.5,1.2,4.3],[0,0.95,0]],
  readn:[[1.3,1.6,4.2],[0,0.95,0],[1.0,1.5,3.6],[0,1.0,0]],
  life:[[0,2.1,8.8],[0,1.0,0],[0,6.5,26],[0,0.6,0]],
  window:[[0.95,1.3,3.9],[0,1.55,-1.0],[0.75,1.3,3.4],[0,1.55,-1.0]],
  desk:[[2.4,1.55,3.6],[0,0.85,-0.2],[2.15,1.5,3.2],[0,0.85,-0.2]],
  bed:[[-1.7,1.25,4.6],[0.1,0.7,0.1],[-1.4,1.22,4.2],[0.1,0.7,0.1]],
  read2:[[-0.5,1.9,3.5],[0,1.1,0.05],[-0.6,1.85,3.0],[0,1.12,0.05]],
  wide:[[0,1.7,6.2],[0,1.0,0],[0,2.1,8.8],[0,1.0,0]],
  mirror:[[0.9,1.6,2.6],[-0.1,1.35,-1.55],[0.3,1.68,-0.22],[-0.06,1.64,-1.55]] };   // one slow push over his shoulder onto the reflection's open eyes
const POV={read:1,window:1,desk:1,bed:1};   // V3.1: these shots are what HE sees, so the blinks black out the viewer's own view
const PROPS={read:'chair',read2:'chair',readn:'chair',wide:'chair',life:'chair',window:'window',desk:'desk',bed:'bed',mirror:'mirror'};

function setT(t){ const sh=shotAt(t); const id=sh.id; const u=sm5(clamp((t-sh.t0)/(sh.t1-sh.t0)));
  ST.GU.uLid.value=(id==='eye'||id==='brain')?0:(id==='eyehook'?(t<0.14?lidAt(t):0):lidAt(t));
  for(const k of ['chair','window','desk','bed','mirror']) G[k].visible=(PROPS[id]===k);
  rbook.visible=mug.visible=phone.visible=false; phoneLight.intensity=0; lapLight.intensity=0; winLight.intensity=0; eyeLight.intensity=0; eyeSpot.intensity=0;
  EYE.visible=id==='eye'||id==='eyehook'; BRAIN.visible=false; BRAIN2.visible=id==='brain';
  if(sh.tod){ let L=TOD[sh.tod]; if(id==='life'){ const cyc=['morning','noon','evening','night'], f=Math.pow(clamp((t-11.35)/1.4),1.6)*14, i=Math.floor(f), w=f-i;
      const a=TOD[cyc[i%4]], b=TOD[cyc[(i+1)%4]]; L={col:new THREE.Color(a.col).lerp(new THREE.Color(b.col),w).getHex(),k:lerp(a.k,b.k,w)}; if(t<11.35) L=TOD.night; }
    scene.fog.density=id==='life'?lerp(0.085,0.02,u):0.085; ST.spot.color.setHex(L.col); ST.beamU.uCol.value.setHex(L.col); ST.tick(t,0); ST.spot.intensity*=L.k; ST.beamU.uI.value*=L.k;
    if(id==='window') winLight.intensity=6; if(id==='desk'){ lapLight.position.set(0,0.95,-0.35); lapLight.intensity=0.6; }
    const hp=heroPose(t,id); hero.all.forEach(m=>m.visible=true); R.poseFig(hero,hp.J); placeEyes(hp.J,id==='mirror'?false:lidAt(t)>0.45);
    const e=hp.ex; if(e.book){ rbook.visible=true; rbook.position.copy(e.book.pos); rbook.lookAt(e.book.pos.clone().add(e.book.f.clone().multiplyScalar(-1)).add(V(0,0.9,0))); rbook.rotateX(-Math.PI/2); }
    if(e.mug){ mug.visible=true; mug.position.copy(e.mug).add(V(0,0.03,0)); }
    if(e.phone){ phone.visible=true; phone.position.copy(e.phone.pos); phone.lookAt(e.phone.pos.clone().addScaledVector(e.phone.f,-1).add(V(0,0.6,0))); phoneLight.position.copy(e.phone.pos).addScaledVector(e.phone.f,0.25); phoneLight.intensity=0.35; }
    if(POV[id]){ hero.all.forEach(m=>m.visible=false); mug.visible=false; eyes.forEach(e=>e.visible=false); const sway=V(0.005*Math.sin(t*1.3),0.004*Math.sin(t*1.7+1),0); let cp, tg;
      if(id==='read'){ tg=e.book.pos.clone(); cp=tg.clone().addScaledVector(e.book.f,-0.22).add(V(0,0.5,0)); rbook.position.copy(tg); rbook.lookAt(cp); rbook.rotateX(Math.PI/2); }   // pages square to his eyes
      else if(id==='window'){ tg=V(0.05,1.5,-1.45); cp=V(0.1,1.45,-0.35); }
      else if(id==='desk'){ tg=V(0,0.93,-0.6); cp=V(0.03,1.12,-0.02); }
      else { tg=e.phone.pos.clone(); cp=tg.clone().addScaledVector(e.phone.f,-0.3).add(V(0,0.14,0)); }
      ST.cam.fov=id==='window'?56:44; ST.cam.updateProjectionMatrix(); ST.cam.position.copy(cp.add(sway)); ST.cam.lookAt(tg.add(V(0,0.01*Math.sin(t*0.9),0))); return; }
    const cm=CAMS[id]; const pos=V(...cm[0]).lerp(V(...cm[2]),u), look=V(...cm[1]).lerp(V(...cm[3]),u);
    ST.cam.fov=38; ST.cam.updateProjectionMatrix(); ST.cam.position.copy(pos); ST.cam.lookAt(look); return; }
  hero.all.forEach(m=>m.visible=false); eyes.forEach(e=>e.visible=false); scene.fog.density=0.012; ST.tick(t,0);
  if(id==='eye'||id==='eyehook'){ eyeSpot.intensity=26; eyeLight.position.set(62.2,0.8,3.2); eyeLight.color.setHex(0x9fb2d6); eyeLight.intensity=0.8;
    let shut=0; for(const e of EYEBLINKS){ const b=t-e; shut=Math.max(shut,b<0||b>0.34?0:(b<0.09?sm5(b/0.09):(b<0.16?1:1-sm5((b-0.16)/0.18)))); } EYEM.update(1-shut,t);
    if(id==='eyehook'){ const k=sm5(clamp(t/2.4)); ST.cam.fov=30; ST.cam.updateProjectionMatrix(); EYEM.cornea.visible=shut<0.6; ST.cam.position.set(60+lerp(0.25,-0.1,k),lerp(0.35,0.15,k),lerp(6.6,5.4,k)); ST.cam.lookAt(60,-0.05,0); return; }
    const pu=sstep(13.95,14.6,t); const k=sm5(clamp((t-13)/1.0)); const z=lerp(lerp(8.2,7.0,k),1.16,Math.pow(pu,1.5)); ST.cam.fov=lerp(30,26,pu); ST.cam.updateProjectionMatrix(); EYEM.cornea.visible=pu<0.55&&shut<0.6;
    ST.cam.position.set(60+lerp(-1.6,-1.0,k)*(1-pu),lerp(0.6,0.3,k)*(1-pu),z); ST.cam.lookAt(60,0,0); return; }
  const dip=b=>{ const x=t-b; return x<-0.05||x>0.35?0:(x<0?sm5((x+0.05)/0.05):(x<0.15?1:1-sm5((x-0.15)/0.2))); };
  const off=Math.max(...BRAINBLINKS.map(dip)); b2U.uT.value=t; b2U.uB.value=sstep(14.6,14.95,t)*(1-0.82*off); b2U.uOcc.value=1-off;
  const v=clamp((t-14.6)/2.4), a=lerp(-2.35,-1.75,sm5(v)); const d=lerp(5.6,4.8,sm5(v)); ST.cam.fov=36; ST.cam.updateProjectionMatrix(); ST.cam.position.set(180+Math.sin(a)*d,0.55-0.25*v,Math.cos(a)*d); ST.cam.lookAt(180,0.3,-0.25); }
window.renderAt=(t,K=3)=>{ const sh=shotAt(t); return ST.renderAt(setT,t,K,{t0:sh.t0,t1:sh.t1,shutter:1/60}); };
window.events={DUR,BLINKS,EYEBLINKS,BRAINBLINKS,SHOTS}; window.ready=true;
