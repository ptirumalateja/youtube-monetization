// He Taught You to Walk (Tiny Stick Tales), look stills, 5 Nov 2026.
// Side-view pictogram figures in Teja's reference style (One Came v4): solid filled shapes, a round head floating above the
// shoulders, tapered capsule limbs, and real transparent gaps where parts overlap. No outlines, no faces: posture carries it.
// One warm living room seen side-on, two eras: 25 years ago (toys, dad standing) and now (two armchairs, phone, cane).
//   ?shot=hook | steps | tries | hold
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920; const SHOT=q.get('shot')||'hook';
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080;
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const FL=1500;                                       // floor line
const COL={dad:'#f3e3c6', oldDad:'#ddd2c0', son:'#e6ecf5'};
const WARM='255,184,112', COOL='190,210,255';

// ---------------------------------------------------------------- helpers
function rr(c,x,y,w,h,r){ c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r); c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath(); }
function glow(x,y,r,c,a){ g.save(); g.globalCompositeOperation='lighter'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},${a})`); rg.addColorStop(0.4,`rgba(${c},${a*0.35})`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); g.restore(); }

// ---------------------------------------------------------------- the room
function room(era){
  // back wall: warm plaster, lighter toward the lamp, never near-black at the edges
  let gr=g.createLinearGradient(0,0,0,FL); gr.addColorStop(0,'#3a2a22'); gr.addColorStop(1,'#56402f'); g.fillStyle=gr; g.fillRect(0,0,1080,FL);
  glow(930,780,900,WARM,0.22);
  // skirting + wooden floor
  g.fillStyle='#2e221b'; g.fillRect(0,FL-14,1080,14);
  gr=g.createLinearGradient(0,FL,0,1920); gr.addColorStop(0,'#4a3326'); gr.addColorStop(1,'#33241c'); g.fillStyle=gr; g.fillRect(0,FL,1080,420);
  g.strokeStyle='rgba(20,12,8,0.35)'; g.lineWidth=3; for(let i=0;i<7;i++){ const y=FL+30+i*i*9+i*22; g.beginPath(); g.moveTo(0,y); g.lineTo(1080,y); g.stroke(); }
  // rug
  g.fillStyle=era===0?'#7a3b2a':'#6a3528'; rr(g,140,FL+6,840,22,8); g.fill(); g.fillStyle='rgba(255,210,160,0.16)'; g.fillRect(170,FL+12,780,4);
  // window (left): dusk sky + soft city bokeh
  const wx=90,wy=560,ww=360,wh=440; gr=g.createLinearGradient(0,wy,0,wy+wh); gr.addColorStop(0,era===0?'#f0b27a':'#3d4a78'); gr.addColorStop(1,era===0?'#e98a5e':'#7a5a78'); g.fillStyle=gr; g.fillRect(wx,wy,ww,wh);
  const R=rng(era?9:4); for(let i=0;i<34;i++){ const x=wx+R()*ww, y=wy+wh*0.55+R()*wh*0.45, r=4+R()*12; const c=R()<0.7?WARM:'255,230,200'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},0.7)`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); }
  g.strokeStyle='#2a1d16'; g.lineWidth=16; g.strokeRect(wx,wy,ww,wh); g.lineWidth=8; g.beginPath(); g.moveTo(wx+ww/2,wy); g.lineTo(wx+ww/2,wy+wh); g.stroke();
  g.fillStyle='#2a1d16'; g.fillRect(wx-20,wy+wh+4,ww+40,14);
  glow(wx+ww/2,wy+wh/2,420,era===0?WARM:COOL,0.10);
  // framed photo on the wall: in "now" it is the toddler holding dad's fingers
  g.fillStyle='#2a1d16'; rr(g,560,600,170,210,6); g.fill(); g.fillStyle=era===0?'#c9a27a':'#d8b98e'; g.fillRect(572,612,146,186);
  if(era===1){ g.fillStyle='#5a4030'; g.beginPath(); g.arc(625,650,11,0,7); g.fill(); g.fillRect(612,665,26,60); g.fillRect(625,700,40,10);
    g.beginPath(); g.arc(675,712,8,0,7); g.fill(); g.fillRect(668,722,14,34); g.fillRect(605,725,10,60); g.fillRect(630,725,10,60); }
  // floor lamp (right)
  g.strokeStyle='#241a14'; g.lineWidth=10; g.beginPath(); g.moveTo(960,FL-10); g.lineTo(960,800); g.stroke(); g.fillStyle='#241a14'; g.beginPath(); g.ellipse(960,FL-8,46,10,0,0,7); g.fill();
  g.fillStyle='#f7d9a6'; g.beginPath(); g.moveTo(890,800); g.lineTo(1030,800); g.lineTo(1002,700); g.lineTo(918,700); g.closePath(); g.fill();
  glow(960,780,700,WARM,0.38); glow(960,770,160,WARM,0.55);
}
function armchair(x,f,{h=1270,col='#7b4a34'}={}){   // side profile; f = the way the sitter faces
  const back=x-f*40, front=x+f*170;
  g.fillStyle='#3a2418'; for(const lx of [back+f*14,front-f*14]) g.fillRect(lx-7,h+70,14,FL-h-70);
  g.fillStyle=col; rr(g,Math.min(back,front)-10,h,Math.abs(front-back)+20,78,26); g.fill();                     // seat cushion
  rr(g,back-f*40-(f>0?0:50)+ (f>0?-10:10),h-330,50,400,24); g.fill();                                         // backrest
  g.fillStyle='rgba(255,210,170,0.12)'; rr(g,Math.min(back,front),h+4,Math.abs(front-back),18,9); g.fill(); }
function blocks(){ const B=[[760,'#d8a34a'],[812,'#5a8ad8'],[786,'#d85a4a']]; B.forEach(([x,c],i)=>{ g.fillStyle=c; const y=i===2?FL+20-120:FL+20-60; rr(g,x-(i===2?-0:0),y,52,52,6); g.fill(); });
  g.fillStyle='#e9d26a'; g.beginPath(); g.arc(900,FL+40,30,0,7); g.fill(); }
function cane(x,y){ g.strokeStyle='#8a5a36'; g.lineWidth=14; g.lineCap='round'; g.beginPath(); g.moveTo(x,y); g.lineTo(x+40,FL+10); g.stroke(); g.beginPath(); g.arc(x-14,y,14,Math.PI*0.0,Math.PI*1.1,true); g.stroke(); }

// ---------------------------------------------------------------- pictogram figure (side view)
const LAY=document.createElement('canvas'); LAY.width=W; LAY.height=H; const f=LAY.getContext('2d');
const GAP=8;
function capsule(c,a,b,ra,rb){ const ang=Math.atan2(b[1]-a[1],b[0]-a[0]); c.moveTo(a[0]+Math.cos(ang+Math.PI/2)*ra,a[1]+Math.sin(ang+Math.PI/2)*ra);
  c.arc(a[0],a[1],ra,ang+Math.PI/2,ang+Math.PI*1.5); c.arc(b[0],b[1],rb,ang-Math.PI/2,ang+Math.PI/2); c.closePath(); }
function part(pathFn,fill){ f.save(); f.globalCompositeOperation='destination-out'; f.beginPath(); pathFn(f); f.lineJoin='round'; f.lineWidth=GAP*2; f.fill(); f.stroke(); f.restore();
  f.beginPath(); pathFn(f); f.fillStyle=fill; f.fill(); }
const Z=1.34, ZC=[560,1215];   // tight framing: zoom the room + figures around this point (text is drawn unzoomed)
const camT=c=>c.setTransform(S*Z,0,0,S*Z,S*(540-Z*ZC[0]),S*(1180-Z*ZC[1]));
function layerBegin(){ f.setTransform(1,0,0,1,0,0); f.clearRect(0,0,W,H); camT(f); }
function layerEnd(a=0.22){ g.save(); g.setTransform(1,0,0,1,0,0); g.shadowColor=`rgba(255,232,200,${a})`; g.shadowBlur=26*S; g.drawImage(LAY,0,0); g.restore(); }
function tint(hex,k){ const h=hex.replace('#',''); const r=parseInt(h.slice(0,2),16), gg=parseInt(h.slice(2,4),16), b=parseInt(h.slice(4,6),16); return `rgb(${r*k|0},${gg*k|0},${b*k|0})`; }
function ik(Sp,T,l1,l2,bend){ const dx=T[0]-Sp[0], dy=T[1]-Sp[1]; const d=Math.min(Math.hypot(dx,dy),l1+l2-0.5), base=Math.atan2(dy,dx);
  const a=Math.acos(Math.max(-1,Math.min(1,(l1*l1+d*d-l2*l2)/(2*l1*d)))); const ang=base+bend*a;
  return [[Sp[0]+l1*Math.cos(ang),Sp[1]+l1*Math.sin(ang)],[Sp[0]+d*Math.cos(base),Sp[1]+d*Math.sin(base)]]; }
const BODY={
  adult:{torso:215,thigh:175,shin:168,up:130,fore:122,head:50,neck:80,rT:[38,50],rL:[26,22,19],rA:[21,18,15]},
  kid:  {torso:96, thigh:64, shin:58, up:52, fore:46, head:38,neck:50,rT:[25,29],rL:[15,13,11],rA:[12,11,10]},
};
// o: {x,y (hip), f (+1 faces right), lean, nod, body, col, legs:{near:[x,y],far:[x,y]}, arms:{near:[x,y],far:[x,y]}, finger:true}
function figure(o){ const B=BODY[o.body||'adult'], fc=o.f, hip=[o.x,o.y];
  const sh=[hip[0]+fc*Math.sin(o.lean||0)*B.torso, hip[1]-Math.cos(o.lean||0)*B.torso];
  const ha=(o.lean||0)+(o.nod||0); const head=[sh[0]+fc*Math.sin(ha)*B.neck, sh[1]-Math.cos(ha)*B.neck];
  const shA=[sh[0]-fc*6,sh[1]+B.rT[1]*0.55];
  const leg=t=>{ const [k,e]=ik(hip,t,B.thigh,B.shin,-fc); return [hip,k,e]; };
  const arm=t=>{ const [el,e]=ik(shA,t,B.up,B.fore,o.elbow??fc); return [shA,el,e]; };
  const L={near:leg(o.legs.near),far:leg(o.legs.far)}, A={near:arm(o.arms.near),far:arm(o.arms.far)};
  const dark=tint(o.col,0.8), main=o.col;
  const limb=(P,r,col,foot)=>part(c=>{ capsule(c,P[0],P[1],r[0],r[1]); capsule(c,P[1],P[2],r[1],r[2]); if(foot){ const e=P[2]; capsule(c,[e[0]-fc*4,e[1]],[e[0]+fc*r[2]*1.8,e[1]+2],r[2],r[2]*0.8); } },col);
  limb(L.far,B.rL,dark,true); limb(A.far,B.rA,dark,false);
  if(o.hunch){ const mid=[hip[0]+fc*Math.sin((o.lean||0)*0.4)*B.torso*0.55-fc*10, hip[1]-Math.cos((o.lean||0)*0.4)*B.torso*0.55];
    part(c=>{ capsule(c,[hip[0],hip[1]-B.rT[0]*0.3],mid,B.rT[0],B.rT[0]*1.12); capsule(c,mid,sh,B.rT[0]*1.12,B.rT[1]); },main); }
  else part(c=>{ capsule(c,[hip[0],hip[1]-B.rT[0]*0.3],sh,B.rT[0],B.rT[1]); },main);
  part(c=>{ c.moveTo(head[0]+B.head,head[1]); c.arc(head[0],head[1],B.head,0,Math.PI*2); },main);
  limb(L.near,B.rL,main,true); limb(A.near,B.rA,main,false);
  if(o.finger){ const h=A.near[2], el=A.near[1]; const d=[h[0]-el[0],h[1]-el[1]], n=Math.hypot(...d); const tip=[h[0]+d[0]/n*30,h[1]+d[1]/n*30];
    part(c=>capsule(c,h,tip,8,6),main); }
  return {hip,sh,head,A,L}; }

// ---------------------------------------------------------------- props held in hands
function phone(x,y,ang,{lit=1,call=false}={}){ g.save(); g.translate(x,y); g.rotate(ang);
  if(lit) { g.restore(); glow(x,y,240,COOL,0.35*lit); g.save(); g.translate(x,y); g.rotate(ang); }
  g.fillStyle='#14161c'; rr(g,-22,-40,44,80,8); g.fill(); g.fillStyle=lit?`rgba(214,228,255,${0.5+0.45*lit})`:'#222'; rr(g,-18,-35,36,70,5); g.fill();
  if(call){ g.fillStyle='#f3c98a'; g.beginPath(); g.arc(0,-8,10,0,7); g.fill(); g.fillRect(-12,4,24,14); g.fillStyle='#4ac47a'; g.beginPath(); g.arc(0,26,5,0,7); g.fill(); }
  g.restore(); }
function sighMarks(x,y,f){ g.save(); g.strokeStyle='rgba(255,240,220,0.75)'; g.lineWidth=5; g.lineCap='round';
  for(let i=0;i<3;i++){ g.beginPath(); g.arc(x+f*(10+i*16),y-6-i*4,12+i*6,-Math.PI*0.35,Math.PI*0.35); g.stroke(); } g.restore(); }
function motionLines(x,y,len,f){ g.save(); g.strokeStyle='rgba(255,240,220,0.5)'; g.lineWidth=5; g.lineCap='round'; for(let i=0;i<3;i++){ g.beginPath(); g.moveTo(x-f*20,y-24+i*24); g.lineTo(x-f*(20+len-i*14),y-24+i*24); g.stroke(); } g.restore(); }

// ---------------------------------------------------------------- text (JetBrains Mono, tracked, cream + gold, like One Came)
const CREAM='255,244,224', GOLD='255,190,110';
function lines(L){ g.setTransform(S,0,0,S,0,0);
  const sc=g.createLinearGradient(0,0,0,560); sc.addColorStop(0,'rgba(30,20,14,0.55)'); sc.addColorStop(1,'rgba(30,20,14,0)'); g.fillStyle=sc; g.fillRect(0,0,1080,560);
  g.textBaseline='top'; g.textAlign='center';
  for(const [s,size,col,y] of L){ g.font=`700 ${size}px "JetBrains Mono"`; g.letterSpacing='6px'; g.save(); g.shadowColor='rgba(0,0,0,0.75)'; g.shadowBlur=22; g.shadowOffsetY=4; g.fillStyle=`rgb(${col})`; g.fillText(s,543,y); g.restore(); }
  g.letterSpacing='0px'; }
function counter(label,n,x=830,y=470){ g.setTransform(S,0,0,S,0,0); g.font='700 40px "JetBrains Mono"'; g.letterSpacing='4px'; const s=`${label} ${n}`; const w=g.measureText(s).width+48;
  g.fillStyle='rgba(30,20,14,0.6)'; rr(g,x-w/2,y,w,70,16); g.fill(); g.fillStyle=`rgb(${GOLD})`; g.textAlign='center'; g.textBaseline='middle'; g.fillText(s,x,y+37); g.letterSpacing='0px'; }

// ---------------------------------------------------------------- shots
const SEAT=1262;
function dadSeated(o={}){ return {x:380,y:SEAT,f:1,lean:0.4,nod:0.22,hunch:1,body:'adult',col:COL.oldDad,legs:{near:[575,FL-20],far:[548,FL-20]},
  arms:{near:o.near||[560,1150],far:o.far||[520,1205]},finger:o.finger,...o.fig}; }
function sonSeated(o={}){ return {x:850,y:SEAT,f:-1,lean:o.lean??0.1,nod:o.nod??0,body:'adult',col:COL.son,legs:{near:[655,FL-20],far:[682,FL-20]},
  arms:{near:o.near||[700,1215],far:o.far||[740,1220]}}; }
const SHOTS={
  // frame 0: the snatch. Dad's finger is left hovering; the son yanks the phone and leans away.
  hook(){ room(1); armchair(380,1); armchair(850,-1,{col:'#5a4a3e'}); cane(250,1120);
    layerBegin(); figure(dadSeated({near:[585,1130],far:[515,1210],finger:true,fig:{nod:0.1}}));
    const s=figure(sonSeated({lean:-0.12,nod:-0.35,near:[735,1165],far:[760,1225]})); layerEnd();
    phone(735,1150,-0.5,{lit:1}); motionLines(735,1150,110,-1); sighMarks(s.head[0]-45,s.head[1]-10,-1);
    lines([['HE TAUGHT YOU',86,CREAM,210],['TO WALK.',104,GOLD,320]]); },
  // 25 years ago: dad bent over, the toddler gripping two of his fingers, wobbling forward
  steps(){ room(0); armchair(170,1,{col:'#9a5a3c'}); blocks();
    layerBegin();
    figure({x:430,y:FL-338,f:1,lean:0.62,nod:0.32,body:'adult',col:COL.dad,legs:{near:[470,FL-20],far:[392,FL-20]},arms:{near:[634,1226],far:[612,1232]}});
    figure({x:668,y:FL-128,f:1,lean:0.12,nod:-0.1,body:'kid',col:COL.son,legs:{near:[712,FL-12],far:[640,FL-12]},arms:{near:[640,1236],far:[628,1240]},elbow:-1});
    layerEnd();
    lines([['5 FALLS.',96,CREAM,230],['ZERO SIGHS.',96,GOLD,340]]); counter('FALLS:',3); },
  // now: dad's finger over the phone, the son already sighing at the 2nd try
  tries(){ room(1); armchair(380,1); armchair(850,-1,{col:'#5a4a3e'}); cane(250,1120);
    layerBegin(); figure(dadSeated({near:[588,1150],far:[566,1172],finger:true,fig:{nod:0.38,lean:0.46}}));
    const s=figure(sonSeated({lean:-0.08,nod:-0.4,near:[742,1238],far:[766,1230]})); layerEnd();
    phone(598,1180,0.25,{lit:1}); sighMarks(s.head[0]-45,s.head[1]-10,-1);
    lines([['YOU SIGHED AT',84,CREAM,210],['THE 2ND TRY.',96,GOLD,320]]); counter('TRIES:',2); },
  // the turn: the son kneels and guides dad's finger like dad guided his steps; the video call connects
  hold(){ room(1); armchair(380,1); cane(250,1120);
    layerBegin(); figure(dadSeated({near:[590,1170],far:[574,1186],finger:true,fig:{nod:0.42,lean:0.46}}));
    figure({x:770,y:FL-205,f:-1,lean:0.16,nod:0.22,body:'adult',col:COL.son,legs:{near:[668,FL-20],far:[905,FL-22]},arms:{near:[604,1168],far:[620,1196]}});
    layerEnd();
    phone(600,1196,0.25,{lit:1.25,call:true});
    lines([['NOW HOLD',100,CREAM,220],['HIS HAND.',112,GOLD,340]]); },
};
function grade(){ g.setTransform(1,0,0,1,0,0);
  const vg=g.createRadialGradient(W/2,H*0.6,W*0.35,W/2,H*0.6,H*0.8); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(28,16,10,0.42)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  const R=rng(7), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*6; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0); }
window.renderAt=()=>{ g.setTransform(S,0,0,S,0,0); g.fillStyle='#3a2a22'; g.fillRect(0,0,1080,1920); camT(g);
  const sh=SHOTS[SHOT]; const T=g.getTransform(); sh(); grade(); return cv.toDataURL('image/jpeg',0.93); };
document.fonts.load('700 40px "JetBrains Mono"').finally(()=>{ window.ready=true; });
