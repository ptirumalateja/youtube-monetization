// The Quiet One: 4.6 s look test of the opening, 5 Nov 2026.
// Target look = Teja's refs 1 and 4: a round matte blue-grey head with a dark outline, big glossy eyes, a navy hoodie with folds,
// black joggers with stripes, white glove hands, a wooden crate, a concrete room. Kept mid-tone (no black edges, FB rule).
// Story beat: each "it's okay" he sends makes his shadow on the wall grow. renderAt(t) is pure.
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920;
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080;
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), lerp=(a,b,u)=>a+(b-a)*u, sm=u=>{u=clamp(u);return u*u*(3-2*u);};
const out3=u=>1-Math.pow(1-clamp(u),3), back=u=>{u=clamp(u); const c=1.9; return 1+(c+1)*Math.pow(u-1,3)+c*Math.pow(u-1,2);};
const ramp=(t,a,b,e=sm)=>e((t-a)/(b-a));
function K(keys,t,e=sm){ if(t<=keys[0][0]) return keys[0][1]; for(let i=1;i<keys.length;i++) if(t<=keys[i][0]){ const u=e((t-keys[i-1][0])/(keys[i][0]-keys[i-1][0])); return lerp(keys[i-1][1],keys[i][1],u); } return keys[keys.length-1][1]; }
function rr(c,x,y,w,h,r){ c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r); c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath(); }
const OUT='#151a26', OW=6;

// ---------------------------------------------------------------- timeline
const DUR=4.6;
const SENDS=[2.35,3.95];                       // "it's okay" sent -> shadow grows
const shadowScale=t=>1.18+0.27*back(ramp(t,SENDS[0],SENDS[0]+0.45,x=>x))+0.30*back(ramp(t,SENDS[1],SENDS[1]+0.45,x=>x));
const look=t=>K([[0,1],[1.15,1],[1.5,0],[1.95,0],[2.1,1],[2.45,1],[2.75,0],[3.45,0],[3.6,1],[4.0,1],[4.25,0]],t); // 1 = down at phone
const smile=t=>K([[0,0.1],[1.4,0.1],[1.7,0.8],[2.0,0.6],[2.7,0.6],[2.95,0.85],[3.4,0.4],[3.6,0.3],[4.2,0.3],[4.45,0.9]],t);
const kick=t=>{ let k=0; for(const s of SENDS){ const u=t-s; if(u>0&&u<0.5) k+=Math.exp(-u*9)*Math.sin(u*70); } return k; };

// ---------------------------------------------------------------- room texture (built once)
const tex=document.createElement('canvas'); tex.width=1080; tex.height=1920; { const c=tex.getContext('2d'), R=rng(11);
  const wg=c.createLinearGradient(0,0,0,1330); wg.addColorStop(0,'#55617a'); wg.addColorStop(1,'#68748c'); c.fillStyle=wg; c.fillRect(0,0,1080,1330);
  for(let i=0;i<260;i++){ const x=R()*1080,y=R()*1330,r=20+R()*120; const rg=c.createRadialGradient(x,y,0,x,y,r); const a=R()*0.07; rg.addColorStop(0,R()<0.5?`rgba(20,26,40,${a})`:`rgba(220,228,240,${a*0.7})`); rg.addColorStop(1,'rgba(0,0,0,0)'); c.fillStyle=rg; c.fillRect(x-r,y-r,2*r,2*r); }
  // faint wall seams
  c.strokeStyle='rgba(25,30,45,0.18)'; c.lineWidth=3; for(const x of [140,980]){ c.beginPath(); c.moveTo(x,0); c.lineTo(x+4,1330); c.stroke(); }
  c.fillStyle='rgba(35,42,58,0.55)'; c.fillRect(0,1300,1080,30);                         // skirting
  const fg=c.createLinearGradient(0,1330,0,1920); fg.addColorStop(0,'#4b566c'); fg.addColorStop(1,'#5d6981'); c.fillStyle=fg; c.fillRect(0,1330,1080,590);
  for(let i=0;i<120;i++){ const x=R()*1080,y=1340+R()*580,r=30+R()*140; const rg=c.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(18,22,34,${R()*0.08})`); rg.addColorStop(1,'rgba(0,0,0,0)'); c.fillStyle=rg; c.fillRect(x-r,y-r,2*r,2*r); }
  const im=c.getImageData(0,0,1080,1920), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*14; d[i]+=n; d[i+1]+=n; d[i+2]+=n*1.1; } c.putImageData(im,0,0); }

// ---------------------------------------------------------------- the character (seated, front view). cx = centre line, sy = seat height
const C={ cx:470, seat:1180, headR:168 };
const HOOD='#27324b', HOOD_D='#1a2236', HOOD_L='#36435f', PANT='#16181f', SKIN='#d7dee9', SKIN_D='#a8b3c4';

function blob(c,pts,fill,stroke=true){ c.beginPath(); c.moveTo(...pts[0]); for(let i=1;i<pts.length;i++){ const p=pts[i]; if(p.length===4) c.quadraticCurveTo(p[0],p[1],p[2],p[3]); else if(p.length===6) c.bezierCurveTo(...p); else c.lineTo(...p); } c.closePath(); c.fillStyle=fill; c.fill(); if(stroke){ c.lineWidth=OW; c.lineJoin='round'; c.strokeStyle=OUT; c.stroke(); } }
function limb(c,pts,w,fill){ c.lineCap='round'; c.lineJoin='round'; c.beginPath(); c.moveTo(...pts[0]); for(let i=1;i<pts.length;i++) c.lineTo(...pts[i]); c.strokeStyle=OUT; c.lineWidth=w+OW*2; c.stroke(); c.strokeStyle=fill; c.lineWidth=w; c.stroke(); }

function legs(c,sil){ const {cx,seat}=C, col=sil||PANT;
  for(const s of [-1,1]){ const kx=cx+s*78, ax=cx+s*92;
    blob(c,[[cx+s*10,seat-10],[kx+s*55,seat+10],[kx+s*58,seat+95,kx+s*40,seat+120],[kx-s*50,seat+120],[kx-s*60,seat+70,cx+s*6,seat+40]],col,!sil); // thigh, foreshortened
    blob(c,[[kx-s*48,seat+95],[kx+s*50,seat+95],[ax+s*46,1490],[ax-s*44,1490]],col,!sil);                                             // shin
    if(!sil){ c.strokeStyle='#cfd6e2'; c.lineWidth=7; c.beginPath(); c.moveTo(kx+s*44,seat+110); c.lineTo(ax+s*40,1480); c.stroke();
      c.strokeStyle='rgba(255,255,255,0.06)'; c.lineWidth=20; c.beginPath(); c.moveTo(kx-s*10,seat+120); c.lineTo(ax-s*8,1470); c.stroke(); }
    blob(c,[[ax-s*50,1478],[ax+s*56,1478],[ax+s*72,1500,ax+s*66,1528],[ax-s*58,1528],[ax-s*66,1505,ax-s*50,1478]],sil||'#2b2f3a',!sil);   // shoe
    if(!sil){ c.fillStyle='#e8ecf2'; c.fillRect(ax-s*60-(s<0?0:0)-60*(s<0?0:0),1516,0,0); c.strokeStyle='#d9dee8'; c.lineWidth=6; c.beginPath(); c.moveTo(ax-s*58,1520); c.lineTo(ax+s*64,1520); c.stroke(); } } }

function torso(c,t,sil){ const {cx,seat}=C, br=Math.sin(t*2*Math.PI/3.2)*4, sh=930+br, col=sil||HOOD;
  blob(c,[[cx-165,sh+30],[cx-150,sh-8,cx-90,sh-16],[cx+90,sh-16],[cx+150,sh-8,cx+165,sh+30],[cx+175,sh+120,cx+158,seat+5],[cx-158,seat+5],[cx-175,sh+120,cx-165,sh+30]],col,!sil);
  if(sil) return;
  // shading: left side lit, right side in shade
  c.save(); c.beginPath(); c.rect(cx+40,sh-20,140,seat-sh+30); c.clip(); c.globalAlpha=0.55; blob(c,[[cx+60,sh],[cx+170,sh+30],[cx+165,seat],[cx+90,seat],[cx+120,sh+150,cx+60,sh]],HOOD_D,false); c.restore();
  c.globalAlpha=0.5; blob(c,[[cx-150,sh+40],[cx-120,sh+10],[cx-95,sh+120],[cx-140,sh+200]],HOOD_L,false); c.globalAlpha=1;
  // hem band
  c.fillStyle=HOOD_D; rr(c,cx-160,seat-38,320,40,14); c.fill(); c.lineWidth=OW; c.strokeStyle=OUT; c.stroke();
  c.strokeStyle='rgba(10,14,24,0.5)'; c.lineWidth=2; for(let x=cx-150;x<cx+155;x+=13){ c.beginPath(); c.moveTo(x,seat-34); c.lineTo(x,seat-2); c.stroke(); }
  // kangaroo pocket
  c.lineWidth=4; c.strokeStyle='rgba(12,16,28,0.8)'; c.beginPath(); c.moveTo(cx-95,seat-40); c.lineTo(cx-70,seat-130); c.lineTo(cx+70,seat-130); c.lineTo(cx+95,seat-40); c.stroke();
  // folds
  c.strokeStyle='rgba(12,16,28,0.55)'; c.lineWidth=3.5; for(const f of [[-60,sh+70,-40,sh+150],[55,sh+60,75,sh+140],[-120,sh+150,-100,sh+210],[118,sh+110,128,sh+180]]){ c.beginPath(); c.moveTo(cx+f[0],f[1]); c.quadraticCurveTo(cx+f[0]+14,(f[1]+f[3])/2,cx+f[2],f[3]); c.stroke(); } }

function hood(c,t,sil){ const {cx}=C, br=Math.sin(t*2*Math.PI/3.2)*4, sh=930+br;
  // the hood bunched behind the neck + collar opening
  blob(c,[[cx-128,sh+6],[cx-150,sh-70,cx-70,sh-80],[cx+70,sh-80],[cx+150,sh-70,cx+128,sh+6],[cx+60,sh+52,cx,sh+56],[cx-60,sh+52,cx-128,sh+6]],sil||HOOD,!sil);
  if(sil) return;
  blob(c,[[cx-74,sh-18],[cx-40,sh-40,cx,sh-42],[cx+40,sh-40,cx+74,sh-18],[cx+40,sh+30,cx,sh+34],[cx-40,sh+30,cx-74,sh-18]],'#0f1422',true);   // opening
  c.fillStyle=SKIN_D; rr(c,cx-34,sh-80,68,90,18); c.fill(); c.lineWidth=OW; c.strokeStyle=OUT; c.stroke();                                        // neck
  c.fillStyle='rgba(15,20,34,0.55)'; c.fillRect(cx-34,sh-20,68,20);
  // drawstrings
  for(const s of [-1,1]){ c.strokeStyle='#d6dce6'; c.lineWidth=6; c.lineCap='round'; c.beginPath(); c.moveTo(cx+s*30,sh+20); c.quadraticCurveTo(cx+s*36,sh+70,cx+s*30+Math.sin(t*1.9+s)*2,sh+112); c.stroke();
    c.fillStyle='#e7ebf1'; rr(c,cx+s*30-5,sh+108,10,20,4); c.fill(); } }

function arms(c,t,sil){ const {cx,seat}=C, br=Math.sin(t*2*Math.PI/3.2)*4, sh=930+br, col=sil||HOOD;
  const tap=t>=1.9&&t<2.35||t>=3.45&&t<3.95?Math.max(0,Math.sin(t*44))*10:0;
  const hy=seat-70+look(t)*0;
  const P={ L:[[cx-150,sh+30],[cx-185,sh+160],[cx-70,hy]], R:[[cx+150,sh+30],[cx+185,sh+160],[cx+70,hy-tap*0.3]] };
  for(const k of ['L','R']) limb(c,P[k],80,col);
  if(sil){ c.fillStyle=sil; c.beginPath(); c.arc(cx-60,hy,40,0,7); c.arc(cx+60,hy,40,0,7); c.fill(); return; }
  for(const k of ['L','R']){ const s=k==='L'?-1:1; c.strokeStyle='rgba(12,16,28,0.5)'; c.lineWidth=3; c.beginPath(); c.moveTo(cx+s*178,sh+120); c.quadraticCurveTo(cx+s*160,sh+150,cx+s*176,sh+175); c.stroke();
    c.save(); c.translate(cx+s*86,hy+2); c.rotate(-s*0.55); c.fillStyle=HOOD_D; rr(c,-20,-34,40,68,10); c.fill(); c.lineWidth=OW-1; c.strokeStyle=OUT; c.stroke(); c.restore(); } // cuffs
  // phone (we see its back) + glow on his face from the screen
  const ph=[cx-46,hy-62,92,150];
  c.save(); c.translate(cx,hy+10); c.rotate(-0.08); c.fillStyle='#1d2230'; rr(c,-46,-75,92,150,16); c.fill(); c.lineWidth=OW-1; c.strokeStyle=OUT; c.stroke(); c.fillStyle='#2f3646'; c.beginPath(); c.arc(-24,-50,9,0,7); c.fill(); c.restore();
  // gloved hands holding it
  for(const s of [-1,1]){ const x=cx+s*52, y=hy+18-(s>0?tap:0);
    c.fillStyle='#eef1f6'; c.beginPath(); c.ellipse(x,y,34,40,s*0.3,0,7); c.fill(); c.lineWidth=OW-1; c.strokeStyle=OUT; c.stroke();
    c.fillStyle='#eef1f6'; c.beginPath(); c.ellipse(x-s*26,y-22-(s>0?tap*0.6:0),12,24,-s*0.6,0,7); c.fill(); c.stroke();      // thumb over the screen
    c.strokeStyle='rgba(120,130,150,0.8)'; c.lineWidth=2.5; for(const d of [-12,2,16]){ c.beginPath(); c.moveTo(x+s*8,y+d); c.lineTo(x+s*28,y+d+2); c.stroke(); } } }

function head(c,t,sil){ const {cx,headR:r}=C, lk=look(t), br=Math.sin(t*2*Math.PI/3.2)*4;
  const hx=cx+lk*4, hy=752+br+lk*26, rot=lk*0.06-0.03*(1-lk);
  c.save(); c.translate(hx,hy); c.rotate(rot);
  if(sil){ c.fillStyle=sil; c.beginPath(); c.arc(0,0,r,0,7); c.fill(); c.restore(); return; }
  const hg=c.createRadialGradient(-r*0.35,-r*0.4,r*0.1,0,0,r*1.05); hg.addColorStop(0,'#eef2f8'); hg.addColorStop(0.55,SKIN); hg.addColorStop(1,'#9aa6b9');
  c.fillStyle=hg; c.beginPath(); c.arc(0,0,r,0,7); c.fill();
  c.save(); c.clip(); c.fillStyle='rgba(60,72,96,0.22)'; c.beginPath(); c.arc(r*0.32,r*0.28,r*0.98,0,7); c.arc(-r*0.1,-r*0.2,r*1.05,0,7,true); c.fill('evenodd'); c.restore();
  // phone-screen glow from below when looking down
  if(lk>0.05){ c.save(); c.beginPath(); c.arc(0,0,r,0,7); c.clip(); const pg=c.createRadialGradient(0,r*1.1,10,0,r*1.0,r*1.1); pg.addColorStop(0,`rgba(190,220,255,${0.35*lk})`); pg.addColorStop(1,'rgba(190,220,255,0)'); c.fillStyle=pg; c.fillRect(-r,-r,2*r,2*r); c.restore(); }
  c.lineWidth=OW+1; c.strokeStyle=OUT; c.beginPath(); c.arc(0,0,r,0,7); c.stroke();
  // face: eyes look down at phone (lk=1) or at camera (lk=0)
  const fy=lk*34, ey=-8+fy, sp=58, sm_=smile(t);
  const blinkU=[1.62,3.0,4.3].reduce((a,b)=>Math.max(a,1-Math.abs(t-b)/0.07),0), lid=clamp(blinkU)+lk*0.35;
  for(const s of [-1,1]){ const ex=s*sp;
    c.fillStyle='#fbfcfe'; c.beginPath(); c.ellipse(ex,ey,33,37,0,0,7); c.fill(); c.lineWidth=4; c.strokeStyle=OUT; c.stroke();
    const px=ex+(lk?0:-2), py=ey+lk*10;
    c.fillStyle='#161b27'; c.beginPath(); c.ellipse(px,py+2,25,28,0,0,7); c.fill();
    c.fillStyle='#fff'; c.beginPath(); c.arc(px-8,py-8,8.5,0,7); c.fill(); c.beginPath(); c.arc(px+9,py+10,4,0,7); c.fill();
    c.fillStyle='rgba(120,160,220,0.25)'; c.beginPath(); c.ellipse(px+4,py+12,13,8,0,0,7); c.fill();
    if(lid>0.01){ c.save(); c.beginPath(); c.ellipse(ex,ey,34,38,0,0,7); c.clip(); c.fillStyle=SKIN; c.fillRect(ex-40,ey-40,80,80*clamp(lid)); c.strokeStyle=OUT; c.lineWidth=4; c.beginPath(); c.moveTo(ex-36,ey-40+80*clamp(lid)); c.lineTo(ex+36,ey-40+80*clamp(lid)); c.stroke(); c.restore();
      c.lineWidth=4; c.strokeStyle=OUT; c.beginPath(); c.ellipse(ex,ey,33,37,0,0,7); c.stroke(); }
    // brows: inner ends raised = the smile doesn't reach the eyes
    const bi=12+sm_*8;
    c.lineCap='round'; c.lineWidth=7; c.beginPath(); c.moveTo(ex-s*30,ey-50+fy*0.1); c.quadraticCurveTo(ex,ey-58,ex+s*-0+(-s)*(-28),ey-52-bi); c.stroke(); }
  // under-eye tired lines
  c.strokeStyle='rgba(70,82,104,0.55)'; c.lineWidth=3; for(const s of [-1,1]){ c.beginPath(); c.arc(s*sp,ey+12,40,0.35*Math.PI,0.65*Math.PI); c.stroke(); }
  // mouth: polite closed smile
  const my=70+fy*0.9, mw=26+sm_*14, mc=sm_*16-6;
  c.lineWidth=6; c.strokeStyle=OUT; c.beginPath(); c.moveTo(-mw,my-mc*0.2); c.quadraticCurveTo(0,my+mc,mw,my-mc*0.2); c.stroke();
  c.lineWidth=3.5; for(const s of [-1,1]){ c.beginPath(); c.moveTo(s*(mw+2),my-mc*0.2-6); c.quadraticCurveTo(s*(mw+8),my-mc*0.2,s*(mw+3),my-mc*0.2+6); c.stroke(); }
  c.restore(); }

function crate(c){ const x=C.cx-150, y=C.seat-4, w=300, h=300;
  c.fillStyle='#8a5f3c'; c.fillRect(x,y,w,h); c.fillStyle='#a0714a'; c.fillRect(x,y,w,26);
  const R=rng(4); c.strokeStyle='rgba(60,36,20,0.55)'; c.lineWidth=3; for(let i=0;i<9;i++){ const yy=y+36+i*30+R()*10; c.beginPath(); c.moveTo(x+8,yy); c.bezierCurveTo(x+w*0.3,yy+R()*12-6,x+w*0.7,yy+R()*12-6,x+w-8,yy+R()*8-4); c.stroke(); }
  c.fillStyle='rgba(50,30,16,0.7)'; c.beginPath(); c.ellipse(x+w*0.7,y+170,14,7,0.2,0,7); c.fill();
  c.fillStyle='rgba(30,20,12,0.35)'; c.fillRect(x+w*0.72,y,w*0.28,h);
  c.lineWidth=OW; c.strokeStyle=OUT; c.strokeRect(x,y,w,h); }

// ---------------------------------------------------------------- shadow: same silhouette, cast up-right onto the wall
const sc=document.createElement('canvas'); sc.width=1080; sc.height=1920; const scx=sc.getContext('2d');
function shadow(t){ const c=scx; c.setTransform(1,0,0,1,0,0); c.clearRect(0,0,1080,1920); const col='#000';
  legs(c,col); torso(c,t,col); arms(c,t,col); hood(c,t,col);
  // the shadow's head does not follow his: it stays up, still, facing us
  c.save(); c.translate(C.cx,0); c.fillStyle=col; c.beginPath(); c.arc(0,752,C.headR,0,7); c.fill(); c.restore();
  const s=shadowScale(t), ax=C.cx+150, ay=1310, sway=Math.sin(t*1.3)*0.012;
  g.save(); g.translate(ax,ay); g.transform(1,0,-0.18+sway,1,0,0); g.scale(s*0.97,s); g.translate(-C.cx,-1480);
  g.filter='blur(7px)'; g.globalAlpha=0.5; g.drawImage(sc,0,0); g.filter='none'; g.restore();
  g.save(); g.globalAlpha=0.32; const fs=g.createRadialGradient(C.cx+60,1505,40,C.cx+60,1505,330); fs.addColorStop(0,'#0c111c'); fs.addColorStop(1,'rgba(12,17,28,0)'); g.fillStyle=fs; g.beginPath(); g.ellipse(C.cx+60,1505,330,60,0,0,7); g.fill(); g.restore(); }

// ---------------------------------------------------------------- UI: messages and captions
function bubble(t,t0,y,from,text,reply,tSend){ const a=out3((t-t0)/0.25); if(a<=0) return; const s=back(clamp((t-t0)/0.3));
  g.save(); g.translate(540,y); g.scale(s,s); g.globalAlpha=a;
  g.shadowColor='rgba(8,12,22,0.45)'; g.shadowBlur=30; g.shadowOffsetY=10; g.fillStyle='#f4f6fa'; rr(g,-330,-70,660,140,38); g.fill(); g.shadowColor='transparent';
  g.fillStyle='#7c8799'; g.font='700 30px "Inter"'; g.textAlign='left'; g.fillText(from,-290,-22); g.fillStyle='#141a26'; g.font='600 40px "Inter"'; g.fillText(text,-290,32);
  g.restore();
  // reply being typed then sent
  if(t>tSend-0.45){ const typed=t<tSend?reply.slice(0,Math.ceil(reply.length*clamp((t-tSend+0.45)/0.4))):reply, sent=t>=tSend, u=out3((t-tSend)/0.2);
    g.save(); g.translate(sent?lerp(540,640,u):540,y+130+(sent?0:10)); g.globalAlpha=a;
    g.font='600 40px "Inter"'; const w=Math.max(120,g.measureText(typed).width+80);
    g.fillStyle=sent?'#3b82f6':'rgba(244,246,250,0.85)'; rr(g,-w/2,-44,w,88,44); g.fill(); g.fillStyle=sent?'#fff':'#8892a4'; g.textAlign='center'; g.fillText(typed+(sent?'':'|'),0,14);
    if(sent){ g.fillStyle='rgba(235,240,248,0.85)'; g.font='600 24px "Inter"'; g.textAlign='right'; g.fillText('Delivered',w/2,74); } g.restore(); } }

const WORDS=[['PSYCHOLOGY',0.05],['SAYS',0.55],['THE',1.0],['MOST',1.2],['DANGEROUS',1.45],['PERSON',1.95],['IS',2.55],['THE',2.7],['ONE',2.85],['WHO',3.05],['ALWAYS',3.25],['SAYS',3.6],["“IT'S",3.9],["OKAY.”",4.15]];
const LINES=[[0,2],[2,6],[6,12],[12,14]];
function captions(t){ let li=0; for(let i=0;i<LINES.length;i++) if(t>=WORDS[LINES[i][0]][1]) li=i; const [a,b]=LINES[li];
  const ws=WORDS.slice(a,b).filter(w=>t>=w[1]); if(!ws.length) return; const big=li===3;
  g.save(); g.font=`900 ${big?118:86}px "Inter"`; g.textAlign='left'; g.textBaseline='middle';
  const lines=[[]]; let lw=0; const maxW=900; for(const w of WORDS.slice(a,b)){ const ww=g.measureText(w[0]+' ').width; if(lw+ww>maxW&&lines[lines.length-1].length){ lines.push([]); lw=0; } lines[lines.length-1].push([...w,ww]); lw+=ww; }
  const y0=1690-(lines.length-1)*55; let active=ws[ws.length-1][0];
  lines.forEach((ln,j)=>{ const tw=ln.reduce((s,w)=>s+w[2],0)-g.measureText(' ').width; let x=540-tw/2; const y=y0+j*(big?130:100);
    for(const w of ln){ if(t>=w[1]){ const pop=back(clamp((t-w[1])/0.16)); g.save(); g.translate(x+w[2]/2,y); g.scale(0.7+0.3*pop,0.7+0.3*pop);
        g.lineJoin='round'; g.lineWidth=14; g.strokeStyle='rgba(6,8,14,0.9)'; g.strokeText(w[0],-w[2]/2,0); g.fillStyle=(w[0]===active||big)?'#ff2b2b':'#ffffff'; g.fillText(w[0],-w[2]/2,0); g.restore(); }
      x+=w[2]; } });
  g.restore(); }

// ---------------------------------------------------------------- frame
window.renderAt=t=>{ g.setTransform(1,0,0,1,0,0);
  const z=1.0+0.07*sm(t/DUR), k=kick(t), cy=1000;
  g.setTransform(S*z,0,0,S*z,W/2-540*S*z+k*6*S,H*cy/1920-cy*S*z+k*4*S);
  g.drawImage(tex,0,0);
  // soft key light on the wall, upper-left of him
  const kl=g.createRadialGradient(330,760,60,330,760,900); kl.addColorStop(0,'rgba(215,228,250,0.32)'); kl.addColorStop(1,'rgba(215,228,250,0)'); g.fillStyle=kl; g.fillRect(-100,-100,1300,2200);
  shadow(t);
  crate(g); legs(g); torso(g,t); hood(g,t); arms(g,t); head(g,t);
  g.setTransform(S,0,0,S,0,0);
  bubble(t,0.18,300,'Rahul',"can't make it tonight, sorry",'it’s okay',SENDS[0]);
  if(t>2.9){ g.save(); g.globalAlpha=1-ramp(t,2.75,2.95); g.restore(); }
  bubble(t,2.85,580,'College group',"lol we forgot to add you",'it’s okay',SENDS[1]);
  captions(t);
  // grade: gentle cool vignette (never near-black at the edges) + grain
  g.setTransform(1,0,0,1,0,0); const vg=g.createRadialGradient(W/2,H*0.45,W*0.4,W/2,H*0.5,H*0.75); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(20,26,42,0.28)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  const R=rng(Math.floor(t*30)+7), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*7; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0);
  return cv.toDataURL('image/jpeg',0.93); };
window.DUR=DUR;
Promise.all([document.fonts.load('900 40px "Inter"'),document.fonts.load('600 40px "Inter"')]).finally(()=>{ window.ready=true; });
