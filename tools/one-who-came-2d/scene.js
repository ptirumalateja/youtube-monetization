// 30 People Said "I'm Here For You." One Came. 2D pictogram version (28 Oct 2026).
// Teja asked for a "well designed" pictogram stickman (safety-sign style: solid shapes, no outlines, a round head floating
// above the shoulders, thin gaps where parts overlap). Seen from behind, like the rain-bench reference: they sit on the far
// edge of the bed, facing the rainy window, so the bed hides the legs and the pose lives in the back, shoulders and head.
// Same dark-warm room (charcoal/navy, one 3000 K lamp on the left, never pure black). The phone is hand-sized.
//   ?shot=hook | count | knock | facedown | payoff
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920; const SHOT=q.get('shot')||'hook';
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080;                                    // everything is authored at 1080x1920
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const C={wall:'#1c2232',wall2:'#131824',floor:'#2a1f1a',warm:'255,180,107',cool:'200,215,255',him:'#e4e9f2',friend:'#f1e2c8'};
const SY=1210;                                     // the far edge of the bed, where they sit
const BASE=1110;                                   // wall meets floor
const CX=430;                                      // him

// ---------------------------------------------------------------- room (seen from behind the bed, looking at the window)
function room(st){
  let gr=g.createLinearGradient(0,0,0,BASE); gr.addColorStop(0,C.wall2); gr.addColorStop(1,C.wall); g.fillStyle=gr; g.fillRect(0,0,1080,BASE);
  g.fillStyle=C.floor; g.fillRect(0,BASE,1080,200); g.fillStyle='#0f0c0a'; g.fillRect(0,BASE-12,1080,12);           // floor strip + skirting
  // the window they look at: rain over a night city
  const wx=230,wy=440,ww=520,wh=480; gr=g.createLinearGradient(0,wy,0,wy+wh); gr.addColorStop(0,'#17233f'); gr.addColorStop(1,'#0e1528'); g.fillStyle=gr; g.fillRect(wx,wy,ww,wh);
  let R=rng(3); for(let i=0;i<80;i++){ const x=wx+R()*ww, y=wy+wh*0.42+R()*wh*0.58, r=3+R()*11; const c=R()<0.7?C.warm:'170,200,255'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},0.8)`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); }
  R=rng(5); g.strokeStyle='rgba(200,215,255,0.33)'; g.lineWidth=2; for(let i=0;i<90;i++){ const x=wx+R()*ww, y=wy+R()*wh, l=14+R()*44; g.beginPath(); g.moveTo(x,y); g.lineTo(x+3,Math.min(wy+wh,y+l)); g.stroke(); }
  g.strokeStyle='#0c0a09'; g.lineWidth=18; g.strokeRect(wx,wy,ww,wh); g.lineWidth=9; g.beginPath(); g.moveTo(wx+ww/2,wy); g.lineTo(wx+ww/2,wy+wh); g.moveTo(wx,wy+wh/2); g.lineTo(wx+ww,wy+wh/2); g.stroke();
  g.fillStyle='#0f0c0a'; g.fillRect(wx-24,wy+wh+6,ww+48,14);                                                       // sill
  glow(wx+ww/2,wy+wh/2,520,C.cool,0.08);
  // door on the right of the back wall: closed (a line of hall light under it) or open with the warm hallway
  const dx=840,dy=560,dw=200,dh=BASE-560;
  if(st.door){ g.fillStyle='#ffd7a0'; g.fillRect(dx,dy,dw,dh); glow(dx+dw/2,dy+dh*0.6,560,C.warm,0.5);
    const wg=g.createLinearGradient(dx,BASE,dx-200,BASE+200); wg.addColorStop(0,'rgba(255,190,120,0.6)'); wg.addColorStop(1,'rgba(255,190,120,0)'); g.fillStyle=wg;
    g.beginPath(); g.moveTo(dx,BASE); g.lineTo(dx+dw,BASE); g.lineTo(dx+dw-60,BASE+200); g.lineTo(dx-260,BASE+200); g.closePath(); g.fill();
    g.fillStyle='#3a2a1e'; g.beginPath(); g.moveTo(dx,dy); g.lineTo(dx-50,dy+16); g.lineTo(dx-50,BASE+18); g.lineTo(dx,BASE); g.closePath(); g.fill(); }   // the leaf, swung in
  else { g.fillStyle='#252b3a'; g.fillRect(dx,dy,dw,dh); g.strokeStyle='#0f0d0b'; g.lineWidth=10; g.strokeRect(dx,dy,dw,dh); g.fillStyle='#8a7350'; g.beginPath(); g.arc(dx+26,dy+dh*0.55,9,0,7); g.fill();
    g.fillStyle='rgba(255,200,140,0.55)'; g.fillRect(dx+6,BASE-4,dw-12,4); }
  // bedside table + the 3000 K lamp (left)
  g.fillStyle='#21180f'; roundRect(20,930,120,190,10); g.fill();
  g.strokeStyle='#3a3026'; g.lineWidth=6; g.beginPath(); g.moveTo(80,930); g.lineTo(80,820); g.stroke();
  g.fillStyle='#f6d7a2'; g.beginPath(); g.moveTo(30,820); g.lineTo(130,820); g.lineTo(108,750); g.lineTo(52,750); g.closePath(); g.fill();
  glow(80,810,760,C.warm,0.44*(st.lamp??1)); glow(80,810,170,C.warm,0.6*(st.lamp??1));
}
// the bed, in front of them (drawn after the people): the quilt runs from their hips toward the camera
function bed(){
  g.fillStyle='rgba(0,0,0,0.35)'; g.fillRect(0,SY-8,1080,14);
  let gr=g.createLinearGradient(0,SY,0,1920); gr.addColorStop(0,'#2a3a66'); gr.addColorStop(1,'#16203c'); g.fillStyle=gr;
  g.beginPath(); g.moveTo(-20,SY+4); g.quadraticCurveTo(540,SY-6,1100,SY+4); g.lineTo(1100,1920); g.lineTo(-20,1920); g.closePath(); g.fill();
  g.strokeStyle='rgba(10,14,28,0.5)'; g.lineWidth=4; for(const [x0,x1] of [[120,40],[560,600],[900,1000]]){ g.beginPath(); g.moveTo(x0,SY+40); g.quadraticCurveTo((x0+x1)/2+30,SY+300,x1,1920); g.stroke(); }  // soft folds
  gr=g.createLinearGradient(0,SY,0,SY+120); gr.addColorStop(0,'rgba(5,6,12,0.55)'); gr.addColorStop(1,'rgba(5,6,12,0)'); g.fillStyle=gr; g.fillRect(0,SY,1080,120);   // the edge falls away
}
function roundRect(x,y,w,h,r){ g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); }
function glow(x,y,r,c,a){ g.save(); g.globalCompositeOperation='lighter'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},${a})`); rg.addColorStop(0.4,`rgba(${c},${a*0.35})`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); g.restore(); }

// ---------------------------------------------------------------- pictogram figure
// Every part is a clean filled shape: tapered capsule limbs, a rounded back, a round head. Parts go onto one shared layer back
// to front, and each new part first cuts a gap of real transparency around itself, so overlaps read as thin slits of the room
// behind, like the white gaps in the reference. A lamp-side gradient and a faint glow finish it. No outlines anywhere.
const FL=document.createElement('canvas'); FL.width=W; FL.height=H; const f=FL.getContext('2d');
const GAP=8;
function capsule(c,a,b,ra,rb){ const ang=Math.atan2(b[1]-a[1],b[0]-a[0]); c.moveTo(a[0]+Math.cos(ang+Math.PI/2)*ra,a[1]+Math.sin(ang+Math.PI/2)*ra);
  c.arc(a[0],a[1],ra,ang+Math.PI/2,ang+Math.PI*1.5); c.arc(b[0],b[1],rb,ang-Math.PI/2,ang+Math.PI/2); c.closePath(); }
function limbPath(c,pts,rs){ for(let i=0;i<pts.length-1;i++) capsule(c,pts[i],pts[i+1],rs[i],rs[i+1]); }
function part(pathFn,fill){ f.save(); f.globalCompositeOperation='destination-out'; f.beginPath(); pathFn(f); f.lineJoin='round'; f.lineWidth=GAP*2; f.fillStyle='#000'; f.strokeStyle='#000'; f.fill(); f.stroke(); f.restore();
  f.beginPath(); pathFn(f); f.fillStyle=fill; f.fill(); }
function shade(col,x0,x1,k=0.78){ const h=col.replace('#',''); const r=parseInt(h.slice(0,2),16), gg=parseInt(h.slice(2,4),16), b=parseInt(h.slice(4,6),16);
  const gr=f.createLinearGradient(x0,0,x1,0); gr.addColorStop(0,`rgb(${r},${gg},${b})`); gr.addColorStop(1,`rgb(${r*k|0},${gg*k|0},${b*k|0})`); return gr; }
function layerBegin(){ f.setTransform(1,0,0,1,0,0); f.clearRect(0,0,W,H); f.setTransform(g.getTransform()); }
function layerEnd(glowA=0.2){ const T=g.getTransform(); g.save(); g.setTransform(1,0,0,1,0,0);
  g.shadowColor=`rgba(255,236,210,${glowA})`; g.shadowBlur=24*S; g.drawImage(FL,0,0); g.restore(); g.setTransform(T); }
// P = {hip, neck, head, arms:[{sh:'L'|'R', e, h, side:'away'|'near'}]}. 'away' arms reach forward (toward the window) so the
// back hides them; 'near' arms come toward the camera (round someone's back) and are drawn over the back.
function figure(P,col,{k=0.78}={}){
  const up=[P.neck[0]-P.hip[0],P.neck[1]-P.hip[1]]; const L=Math.hypot(...up); const u=[up[0]/L,up[1]/L], n=[-u[1],u[0]];
  const at=(p,a,b)=>[p[0]+n[0]*a+u[0]*b,p[1]+n[1]*a+u[1]*b];
  const fill=shade(col,P.hip[0]-120,P.hip[0]+120,k);
  const SH={L:at(P.neck,-44,-24), R:at(P.neck,44,-24)};
  const arm=a=>part(c=>{ limbPath(c,[SH[a.sh],a.e,a.h],[21,17,14]); c.moveTo(a.h[0]+17,a.h[1]); c.arc(a.h[0],a.h[1],17,0,Math.PI*2); },fill);
  const head=()=>part(c=>{ c.moveTo(P.head[0]+46,P.head[1]); c.arc(P.head[0],P.head[1],46,0,Math.PI*2); },fill);
  // the back: broad round shoulders, a slight taper, the seat widening onto the bed
  const back=c=>{ const sL=at(P.neck,-58,-8), sR=at(P.neck,58,-8), wR=at(P.hip,44,70), wL=at(P.hip,-44,70), hR=at(P.hip,54,0), hL=at(P.hip,-54,0), top=at(P.neck,0,8);
    c.moveTo(hL[0],hL[1]); c.lineTo(wL[0],wL[1]); c.bezierCurveTo(...at(P.hip,-50,150),...at(P.neck,-64,-80),...sL); c.quadraticCurveTo(top[0],top[1],sR[0],sR[1]);
    c.bezierCurveTo(...at(P.neck,64,-80),...at(P.hip,50,150),...wR); c.lineTo(hR[0],hR[1]); c.closePath(); };
  const away=(P.arms||[]).filter(a=>a.side!=='near'), near=(P.arms||[]).filter(a=>a.side==='near');
  away.forEach(arm);
  if(P.headLow){ head(); part(back,fill); } else { part(back,fill); head(); }   // a hung head sits behind the shoulders
  near.forEach(arm);
  return {SH,fill}; }
function pose(cx,o={}){ const P={hip:[cx,SY+6]}; P.neck=[cx+(o.neck?.[0]||0),SY+(o.neck?.[1]??-232)]; P.head=[P.neck[0]+(o.head?.[0]||0),P.neck[1]+(o.head?.[1]??-66)];
  P.headLow=!!o.headLow; P.arms=o.arms||[{sh:'L',e:[cx-74,SY-100],h:[cx-60,SY-10]},{sh:'R',e:[cx+74,SY-100],h:[cx+60,SY-10]}]; return P; }

// ---------------------------------------------------------------- phone (hand-sized, on the bed beside him) and message cards
function phone(x,y,{lit=1}={}){
  if(lit){ glow(x,y-20,300,C.cool,0.32); glow(x,y,80,C.cool,0.6); }
  g.save(); g.translate(x,y); g.fillStyle='#0b0c10'; roundRect(-36,-10,72,22,6); g.fill();
  if(lit){ g.fillStyle='rgba(225,235,255,0.95)'; roundRect(-31,-6,62,14,4); g.fill(); }
  g.restore(); }
const MSG=['here for you','call me anytime','sending love','let me know if you need anything','thinking of you',"i'm always here"];
function cards(x,y,n){ g.save(); g.font='600 24px "DejaVu Sans Mono", monospace'; g.textBaseline='middle';
  for(let i=0;i<n;i++){ const t=MSG[i%MSG.length]; const w=Math.max(200,g.measureText(t).width+44), cy=y-70-i*58, a=Math.max(0.35,1-i*0.12), cx=x+((i%2)?-16:16);
    g.globalAlpha=a; g.fillStyle='rgba(236,240,248,0.92)'; roundRect(cx-w/2,cy-21,w,42,14); g.fill(); g.fillStyle='#22262e'; g.fillText(t,cx-w/2+22,cy+1); }
  g.globalAlpha=1; g.fillStyle='#d83a2e'; g.beginPath(); g.arc(x+44,y-26,26,0,7); g.fill(); g.fillStyle='#fff'; g.font='700 26px "DejaVu Sans Mono", monospace'; g.textAlign='center'; g.fillText(String(Math.min(n*5,30)),x+44,y-25); g.restore(); }

// ---------------------------------------------------------------- shots
const SHOTS={
  hook:    {cam:[1.8,480,1050], door:0},
  count:   {cam:[1.75,530,1040], door:0},
  knock:   {cam:[1.3,640,990], door:1},
  facedown:{cam:[1.65,530,1045], door:1},
  payoff:  {cam:[1.9,520,1050], door:1},
};
function render(t){
  const st=SHOTS[SHOT]; g.setTransform(1,0,0,1,0,0); g.fillStyle='#10141c'; g.fillRect(0,0,W,H);
  const [z,fx,fy]=st.cam; g.setTransform(S*z,0,0,S*z,S*540-S*z*fx,S*1150-S*z*fy);
  room(st);
  const PH=[CX+150,SY+40];                                        // on the quilt, just behind him and to his right
  const FX=CX+190;
  if(SHOT==='hook'||SHOT==='count'){
    // elbows on his knees, head hung below the shoulders
    const P=pose(CX,{neck:[0,-196],head:[0,-40],headLow:1,arms:[{sh:'L',e:[CX-96,SY-70],h:[CX-40,SY-150]},{sh:'R',e:[CX+96,SY-70],h:[CX+40,SY-150]}]});
    layerBegin(); figure(P,C.him); layerEnd(0.2); bed(); phone(...PH);
    if(SHOT==='count') cards(PH[0]-10,PH[1]-30,6);
  }
  if(SHOT==='knock'){
    // his head comes up and turns to the door
    const P=pose(CX,{neck:[6,-226],head:[30,-60]});
    // the friend in the doorway, backlit: a dark pictogram against the warm light
    const fx=940, fb=BASE-6; const F={hip:[fx,fb-260],neck:[fx,fb-440],head:[fx,fb-500]};
    layerBegin(); g.save();
    part(c=>{ limbPath(c,[[fx-22,fb-250],[fx-26,fb-130],[fx-30,fb-10]],[22,19,16]); limbPath(c,[[fx+22,fb-250],[fx+26,fb-130],[fx+30,fb-10]],[22,19,16]); },'#2b231c');
    part(c=>{ c.moveTo(fx-52,fb-450); c.lineTo(fx+52,fb-450); c.quadraticCurveTo(fx+60,fb-450,fx+46,fb-250); c.lineTo(fx-46,fb-250); c.quadraticCurveTo(fx-60,fb-450,fx-52,fb-450); c.closePath(); },'#2b231c');
    part(c=>{ limbPath(c,[[fx-58,fb-430],[fx-66,fb-340],[fx-60,fb-260]],[18,16,15]); limbPath(c,[[fx+58,fb-430],[fx+66,fb-340],[fx+60,fb-260]],[18,16,15]); },'#2b231c');
    part(c=>{ c.moveTo(fx+40,fb-500); c.arc(fx,fb-500,40,0,Math.PI*2); },'#2b231c');
    g.restore(); layerEnd(0);
    layerBegin(); figure(P,C.him); layerEnd(0.2); bed(); phone(...PH);
  }
  if(SHOT==='facedown'){
    const P=pose(CX,{neck:[-4,-222],head:[-10,-62]});
    const F=pose(FX,{neck:[-26,-214],head:[-40,-56],arms:[{sh:'L',e:[FX-110,SY-60],h:[PH[0]-4,PH[1]-14],side:'near'},{sh:'R',e:[FX+74,SY-100],h:[FX+60,SY-10]}]});
    layerBegin(); figure(P,C.him); layerEnd(0.2); bed(); phone(...PH,{lit:0});
    layerBegin(); figure(F,C.friend); layerEnd(0.22);
  }
  if(SHOT==='payoff'){
    const FX2=CX+176;
    const F=pose(FX2,{neck:[-6,-232],head:[-10,-66],arms:[{sh:'R',e:[FX2+74,SY-100],h:[FX2+60,SY-10]}]});
    const P=pose(CX,{neck:[38,-210],head:[84,-40],arms:[{sh:'L',e:[CX-74,SY-100],h:[CX-56,SY-10]},{sh:'R',e:[CX+60,SY-96],h:[CX+60,SY-10]}]});
    layerBegin(); const fr=figure(F,C.friend);
    figure(P,C.him);
    // the friend's arm round his back, the hand resting on his far shoulder (over his back, toward us)
    part(c=>{ limbPath(c,[fr.SH.L,[CX+20,P.neck[1]+70],[CX-50,P.neck[1]+18]],[21,17,14]); c.moveTo(CX-50+18,P.neck[1]+18); c.arc(CX-50,P.neck[1]+18,18,0,Math.PI*2); },fr.fill);
    layerEnd(0.22); bed(); phone(...PH,{lit:0});
  }
  // grade: vignette, raised blacks (never #000), grain
  g.setTransform(1,0,0,1,0,0);
  const vg=g.createRadialGradient(W/2,H*0.55,W*0.25,W/2,H*0.55,H*0.75); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(6,8,14,0.7)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  g.fillStyle='rgba(18,22,34,0.10)'; g.fillRect(0,0,W,H);
  const R=rng(Math.floor(t*24)+1), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*7; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0);
}
window.renderAt=(t)=>{ render(t); return cv.toDataURL('image/jpeg',0.94); };
window.ready=true;
