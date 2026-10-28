// 30 People Said "I'm Here For You." One Came. 2D version (28 Oct 2026). Teja asked for a free-flowing 2D stickman instead of the
// cylinder rig: thick round strokes, soft glow, curved limbs, no face. Same dark-warm room (charcoal/navy, one 3000 K lamp,
// rain on the window), drawn flat on a canvas. The phone is hand-sized (about 0.7 head widths).
//   ?shot=hook | count | knock | facedown | payoff
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920; const SHOT=q.get('shot')||'hook';
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080;                                    // everything is authored at 1080x1920
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const C={wall:'#1b2130',wall2:'#141925',floor:'#2a1f1a',floor2:'#16120f',warm:'255,180,107',cool:'200,215,255',him:'#e6ebf3',friend:'#f2e4cc'};
const SY=1180, FY=1440;                            // the bed edge they sit on, the floor their feet are on
const CX=360;                                      // him

// ---------------------------------------------------------------- room
function room(st){
  // back wall + floor
  let gr=g.createLinearGradient(0,0,0,1150); gr.addColorStop(0,C.wall2); gr.addColorStop(1,C.wall); g.fillStyle=gr; g.fillRect(0,0,1080,1150);
  gr=g.createLinearGradient(0,1150,0,1920); gr.addColorStop(0,C.floor); gr.addColorStop(1,C.floor2); g.fillStyle=gr; g.fillRect(0,1150,1080,770);
  g.strokeStyle='rgba(0,0,0,0.25)'; g.lineWidth=2; for(let i=0;i<9;i++){ const y=1150+Math.pow(i/8,1.6)*770; g.beginPath(); g.moveTo(0,y); g.lineTo(1080,y); g.stroke(); }
  g.fillStyle='#0f0c0a'; g.fillRect(0,1138,1080,14);                                         // skirting
  // window with rain over a night city
  const wx=150,wy=520,ww=400,wh=360; gr=g.createLinearGradient(0,wy,0,wy+wh); gr.addColorStop(0,'#16223f'); gr.addColorStop(1,'#0d1426'); g.fillStyle=gr; g.fillRect(wx,wy,ww,wh);
  let R=rng(3); for(let i=0;i<60;i++){ const x=wx+R()*ww, y=wy+wh*0.45+R()*wh*0.55, r=3+R()*10; const c=R()<0.7?C.warm:'170,200,255'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},0.8)`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); }
  R=rng(5); g.strokeStyle='rgba(200,215,255,0.35)'; g.lineWidth=2; for(let i=0;i<70;i++){ const x=wx+R()*ww, y=wy+R()*wh, l=14+R()*40; g.beginPath(); g.moveTo(x,y); g.lineTo(x+3,Math.min(wy+wh,y+l)); g.stroke(); }
  g.strokeStyle='#0c0a09'; g.lineWidth=16; g.strokeRect(wx,wy,ww,wh); g.lineWidth=8; g.beginPath(); g.moveTo(wx+ww/2,wy); g.lineTo(wx+ww/2,wy+wh); g.moveTo(wx,wy+wh/2); g.lineTo(wx+ww,wy+wh/2); g.stroke();
  glow(wx+ww/2,wy+wh/2,420,C.cool,0.07);
  // door (right), closed or open with the hallway light
  const dx=790,dy=640,dw=220,dh=510;
  if(st.door){ g.fillStyle='#ffd7a0'; g.fillRect(dx,dy,dw,dh); glow(dx+dw/2,dy+dh*0.6,520,C.warm,0.45);
    // the light wedge on the floor, toward him
    const wg=g.createLinearGradient(dx,1150,CX,1700); wg.addColorStop(0,'rgba(255,190,120,0.55)'); wg.addColorStop(1,'rgba(255,190,120,0)'); g.fillStyle=wg;
    g.beginPath(); g.moveTo(dx,1150); g.lineTo(dx+dw,1150); g.lineTo(1080,1920); g.lineTo(CX-40,1920); g.closePath(); g.fill();
    g.fillStyle='#3a2a1e'; g.beginPath(); g.moveTo(dx+dw,dy); g.lineTo(dx+dw+60,dy-20); g.lineTo(dx+dw+60,dy+dh+30); g.lineTo(dx+dw,dy+dh); g.closePath(); g.fill(); }  // the leaf, swung in
  else { g.fillStyle='#262c3a'; g.fillRect(dx,dy,dw,dh); g.strokeStyle='#0f0d0b'; g.lineWidth=10; g.strokeRect(dx,dy,dw,dh); g.fillStyle='#8a7350'; g.beginPath(); g.arc(dx+28,dy+dh*0.55,9,0,7); g.fill();
    g.fillStyle='rgba(255,200,140,0.5)'; g.fillRect(dx+6,dy+dh-4,dw-12,4); }                                         // a thin line of hallway light under the door
  // bed against the wall, behind him
  g.fillStyle='#ebe5d8'; roundRect(90,1050,170,70,26); g.fill();                              // pillows against the wall
  g.fillStyle='#24345e'; roundRect(60,1100,700,90,30); g.fill();                               // quilt, top of the bed
  g.fillStyle='#d9d2c4'; roundRect(60,1170,700,40,14); g.fill();                               // mattress edge they sit on
  g.fillStyle='#1d1814'; roundRect(60,1205,700,150,18); g.fill();                              // bed frame front
  g.fillStyle='rgba(0,0,0,0.35)'; g.fillRect(60,1350,700,20);                                  // contact shadow
  // bedside table + the 3000 K lamp (left)
  g.fillStyle='#21180f'; roundRect(-20,1000,90,200,10); g.fill();
  g.strokeStyle='#3a3026'; g.lineWidth=6; g.beginPath(); g.moveTo(25,1000); g.lineTo(25,900); g.stroke();
  g.fillStyle='#f6d7a2'; g.beginPath(); g.moveTo(-15,900); g.lineTo(65,900); g.lineTo(45,840); g.lineTo(5,840); g.closePath(); g.fill();
  glow(25,890,700,C.warm,0.42*(st.lamp??1)); glow(25,890,160,C.warm,0.6*(st.lamp??1));
  // a frame on the wall
  g.strokeStyle='#2c241b'; g.lineWidth=10; g.strokeRect(610,420,130,170); g.fillStyle='#232a38'; g.fillRect(615,425,120,160);
}
function roundRect(x,y,w,h,r){ g.beginPath(); g.moveTo(x+r,y); g.arcTo(x+w,y,x+w,y+h,r); g.arcTo(x+w,y+h,x,y+h,r); g.arcTo(x,y+h,x,y,r); g.arcTo(x,y,x+w,y,r); g.closePath(); }
function glow(x,y,r,c,a){ g.save(); g.globalCompositeOperation='lighter'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},${a})`); rg.addColorStop(0.4,`rgba(${c},${a*0.35})`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); g.restore(); }

// ---------------------------------------------------------------- the stickman: curved thick strokes, round caps, soft glow
// pose = {hip, neck, head, kL,kR, fL,fR, eL,eR, hL,hR} in px; bend = how far the limb curves through its joint
function curve(a,b,c,w,col){ g.strokeStyle=col; g.lineWidth=w; g.lineCap='round'; g.lineJoin='round'; g.beginPath(); g.moveTo(a[0],a[1]);
  // a smooth curve that passes through b (the joint): control point pushed past b so the stroke actually reaches it
  const cx=2*b[0]-(a[0]+c[0])/2, cy=2*b[1]-(a[1]+c[1])/2; g.quadraticCurveTo(cx,cy,c[0],c[1]); g.stroke(); }
function figure(P,col,{glowA=0.35,order='default',skipArm=null}={}){
  const legW=30, armW=24, torsoW=36, hr=48, OL='rgba(14,17,26,0.7)';
  const hipL=[P.hip[0]-22,P.hip[1]], hipR=[P.hip[0]+22,P.hip[1]];
  const shL=[P.neck[0]-46,P.neck[1]+20], shR=[P.neck[0]+46,P.neck[1]+20];
  // every part is drawn twice: a thin dark outline, then the colour with a soft glow, so overlapping parts stay readable
  const part=(fn)=>{ g.save(); g.shadowBlur=0; fn(OL,7); g.restore(); g.save(); g.shadowColor=`rgba(255,240,220,${glowA})`; g.shadowBlur=24; fn(col,0); g.restore(); };
  const leg=(h,k,f)=>part((c,o)=>{ g.strokeStyle=c; g.lineWidth=legW+o; g.lineCap='round'; g.lineJoin='round'; g.beginPath(); g.moveTo(h[0],h[1]); g.lineTo(k[0],k[1]); g.quadraticCurveTo(k[0]+(f[0]-k[0])*0.2,k[1]+(f[1]-k[1])*0.5,f[0],f[1]); g.stroke();
    g.fillStyle=c; g.beginPath(); g.ellipse(f[0]+(f[0]>P.hip[0]?6:-6),f[1]+2,26+o/2,15+o/2,0,0,7); g.fill(); });
  leg(hipL,P.kL,P.fL); leg(hipR,P.kR,P.fR);
  part((c,o)=>{ g.strokeStyle=c; g.lineCap='round'; g.lineWidth=torsoW+o; g.beginPath(); g.moveTo(P.hip[0],P.hip[1]); g.quadraticCurveTo(P.hip[0]+(P.bow||0),(P.hip[1]+P.neck[1])/2,P.neck[0],P.neck[1]); g.stroke();
    g.lineWidth=armW*1.6+o; g.beginPath(); g.moveTo(shL[0],shL[1]); g.quadraticCurveTo(P.neck[0],P.neck[1]-6,shR[0],shR[1]); g.stroke(); });
  const head=()=>part((c,o)=>{ g.fillStyle=c; g.beginPath(); g.arc(P.head[0],P.head[1],hr+o/2,0,7); g.fill(); });
  const arm=(sh,e,h)=>part((c,o)=>{ g.strokeStyle=c; g.lineWidth=armW+o; g.lineCap='round'; g.lineJoin='round'; g.beginPath(); g.moveTo(sh[0],sh[1]); const cx=2*e[0]-(sh[0]+h[0])/2, cy=2*e[1]-(sh[1]+h[1])/2; g.quadraticCurveTo(cx,cy,h[0],h[1]); g.stroke(); });
  const arms=()=>{ if(skipArm!=='L') arm(shL,P.eL,P.hL); if(skipArm!=='R') arm(shR,P.eR,P.hR); };
  if(order==='headFirst'){ head(); arms(); } else { arms(); head(); }
  return {shL,shR}; }
// sitting on the bed edge, front view: short foreshortened thighs, shins down to the floor (like the bench in the reference)
function seated(cx,o={}){ const hipY=SY-14;
  const P={hip:[cx,hipY], kL:[cx-48,SY+24], kR:[cx+48,SY+24], fL:[cx-58,FY], fR:[cx+58,FY], bow:o.bow||0};
  P.neck=o.neck?[cx+o.neck[0],SY+o.neck[1]]:[cx,SY-232]; P.head=o.head?[P.neck[0]+o.head[0],P.neck[1]+o.head[1]]:[P.neck[0],P.neck[1]-78];
  P.eL=o.eL||[cx-74,SY-70]; P.hL=o.hL||[cx-50,SY+16]; P.eR=o.eR||[cx+74,SY-70]; P.hR=o.hR||[cx+50,SY+16];
  return P; }

// ---------------------------------------------------------------- phone (hand-sized) and message cards
function phone(x,y,{lit=1,down=0}={}){
  if(lit){ glow(x,y-30,330,C.cool,0.30); glow(x,y-6,90,C.cool,0.55); }
  g.save(); g.translate(x,y); g.fillStyle='#0b0c10'; roundRect(-34,-9,68,14,5); g.fill();
  if(lit&&!down){ g.fillStyle='rgba(225,235,255,0.95)'; roundRect(-30,-10,60,6,3); g.fill(); }
  g.restore(); }
const MSG=['here for you','call me anytime','sending love','let me know if you need anything','thinking of you',"i'm always here"];
function cards(x,y,n){ g.save(); g.font='600 24px "DejaVu Sans Mono", monospace'; g.textBaseline='middle';
  for(let i=0;i<n;i++){ const t=MSG[i%MSG.length]; const w=Math.max(200,g.measureText(t).width+44), cy=y-60-i*58, a=Math.max(0.35,1-i*0.12), cx=x+((i%2)?-22:18);
    g.globalAlpha=a; g.fillStyle='rgba(236,240,248,0.92)'; roundRect(cx-w/2,cy-21,w,42,14); g.fill(); g.fillStyle='#22262e'; g.fillText(t,cx-w/2+22,cy+1); }
  g.globalAlpha=1; g.fillStyle='#d83a2e'; g.beginPath(); g.arc(x+46,y-32,26,0,7); g.fill(); g.fillStyle='#fff'; g.font='700 26px "DejaVu Sans Mono", monospace'; g.textAlign='center'; g.fillText(String(Math.min(n*5,30)),x+46,y-31); g.restore(); }

// ---------------------------------------------------------------- shots
const SHOTS={
  hook:    {cam:[1.05,520,1120], door:0},
  count:   {cam:[1.4,480,1170], door:0},
  knock:   {cam:[1.0,560,1080], door:1},
  facedown:{cam:[1.45,470,1180], door:1},
  payoff:  {cam:[1.75,450,1150], door:1},
};
function render(t){
  const st=SHOTS[SHOT]; g.setTransform(1,0,0,1,0,0); g.fillStyle='#10141c'; g.fillRect(0,0,W,H);
  const [z,fx,fy]=st.cam;   // zoom, focus point (kept at x=540, y=1150 of the frame)
  g.setTransform(S*z,0,0,S*z,S*540-S*z*fx,S*1150-S*z*fy);
  room(st);
  const PH=[CX+108,SY-2];                                         // on the bed beside him
  if(SHOT==='hook'||SHOT==='count'){
    // elbows on knees, head hung, hands at his head
    const P=seated(CX,{neck:[0,-200],head:[0,44],eL:[CX-80,SY+4],hL:[CX-44,SY-162],eR:[CX+80,SY+4],hR:[CX+44,SY-162]});
    phone(...PH); figure(P,C.him,{glowA:0.25,order:'headFirst'});
    if(SHOT==='count') cards(PH[0]+30,PH[1]-40,6);
  }
  if(SHOT==='knock'){
    const P=seated(CX,{neck:[8,-228],head:[24,-74]});
    phone(...PH); figure(P,C.him,{glowA:0.25});
    // the friend in the doorway, backlit
    const fx=905, fb=1150; const F={hip:[fx,fb-300],neck:[fx,fb-500],head:[fx,fb-566],kL:[fx-20,fb-150],kR:[fx+18,fb-150],fL:[fx-30,fb-4],fR:[fx+28,fb-4],eL:[fx-60,fb-390],hL:[fx-56,fb-290],eR:[fx+60,fb-390],hR:[fx+58,fb-290]};
    figure(F,'#2a221b',{glowA:0.9});
  }
  if(SHOT==='facedown'||SHOT==='payoff'){
    const FX=SHOT==='payoff'?CX+180:CX+236;
    if(SHOT==='facedown'){
      phone(...PH,{lit:0,down:1});
      const P=seated(CX,{neck:[6,-224],head:[14,-70]}); figure(P,C.him,{glowA:0.2});
      const F=seated(FX,{neck:[-18,-218],head:[-30,-70],eL:[FX-96,SY-110],hL:[PH[0]+8,PH[1]-12]});
      figure(F,C.friend,{glowA:0.35});
    } else {
      phone(...PH,{lit:0,down:1});
      const F=seated(FX,{neck:[0,-232],head:[-16,-74]});
      const P=seated(CX,{neck:[40,-206],head:[76,-26],eL:[CX-26,SY-84],hL:[CX-34,SY+14],eR:[CX+96,SY-84],hR:[CX+64,SY+16]});
      figure(F,C.friend,{glowA:0.35,skipArm:'L'});
      const fsh=[F.neck[0]-46,F.neck[1]+20]; g.save(); g.shadowColor='rgba(255,240,220,0.35)'; g.shadowBlur=26;
      curve(fsh,[CX+80,P.neck[1]-14],[CX-2,P.neck[1]+22],24,C.friend); g.restore();     // his arm goes behind
      figure(P,C.him,{glowA:0.25});
      g.save(); g.strokeStyle='rgba(14,17,26,0.7)'; g.lineWidth=5; g.fillStyle=C.friend; g.beginPath(); g.ellipse(CX-6,P.neck[1]+22,22,14,-0.4,0,7); g.fill(); g.stroke(); g.restore();   // his hand on the far shoulder
    }
  }
  // grade: vignette, raised blacks (never #000), grain
  g.setTransform(1,0,0,1,0,0);
  const vg=g.createRadialGradient(W/2,H*0.55,W*0.25,W/2,H*0.55,H*0.75); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(6,8,14,0.7)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  g.fillStyle='rgba(18,22,34,0.10)'; g.fillRect(0,0,W,H);
  const R=rng(Math.floor(t*24)+1), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*7; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0);
}
window.renderAt=(t)=>{ render(t); return cv.toDataURL('image/jpeg',0.94); };
window.ready=true;
