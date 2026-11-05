// "Psychology says the most dangerous anger..." shot-for-shot remake of Teja's ref 2 (5 Nov 2026).
// 7 shots, line stickman (white shaded round head, thin black limbs), cinematic dark backgrounds, red/white word captions.
// Backgrounds: alley + park are CC BY photos (bg/credits.txt), the rest are painted here. renderAt(t) is pure.
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920;
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080;
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), lerp=(a,b,u)=>a+(b-a)*u, sm=u=>{u=clamp(u);return u*u*(3-2*u);};
const out3=u=>1-Math.pow(1-clamp(u),3), back=u=>{u=clamp(u); const c=1.7; return 1+(c+1)*Math.pow(u-1,3)+c*Math.pow(u-1,2);};
const ramp=(t,a,b,e=sm)=>e((t-a)/(b-a));
function K(keys,t,e=sm){ if(t<=keys[0][0]) return keys[0][1]; for(let i=1;i<keys.length;i++) if(t<=keys[i][0]){ const u=e((t-keys[i-1][0])/(keys[i][0]-keys[i-1][0])); const a=keys[i-1][1], b=keys[i][1]; return Array.isArray(a)?a.map((v,j)=>lerp(v,b[j],u)):lerp(a,b,u); } return keys[keys.length-1][1]; }
function mk(w,h){ const c=document.createElement('canvas'); c.width=w; c.height=h; return c; }
function rad(c,x,y,r,stops){ const gr=c.createRadialGradient(x,y,0,x,y,r); stops.forEach(([o,col])=>gr.addColorStop(o,col)); return gr; }
function glow(c,x,y,r,col,a){ c.save(); c.globalCompositeOperation='lighter'; c.fillStyle=rad(c,x,y,r,[[0,`rgba(${col},${a})`],[0.35,`rgba(${col},${a*0.35})`],[1,`rgba(${col},0)`]]); c.fillRect(x-r,y-r,2*r,2*r); c.restore(); }
// value-noise fbm canvas (grey), for clouds / concrete / grime
function noiseCanvas(w,h,cell,oct,seed){ const c=mk(w,h), x=c.getContext('2d'), R=rng(seed);
  for(let o=0;o<oct;o++){ const cs=cell/Math.pow(2,o), nx=Math.ceil(w/cs)+2, ny=Math.ceil(h/cs)+2, s=mk(nx,ny), sx=s.getContext('2d'), im=sx.createImageData(nx,ny);
    for(let i=0;i<nx*ny;i++){ const v=R()*255; im.data[i*4]=im.data[i*4+1]=im.data[i*4+2]=v; im.data[i*4+3]=255; } sx.putImageData(im,0,0);
    x.globalAlpha=o===0?1:0.5/o; x.imageSmoothingEnabled=true; x.imageSmoothingQuality='high'; x.drawImage(s,0,0,nx*cs,ny*cs); }
  return c; }
const IMG={}; const loadImg=n=>new Promise(r=>{ const i=new Image(); i.onload=()=>{IMG[n]=i;r();}; i.onerror=()=>r(); i.src='bg/'+n+'.jpg'; });
function cover(c,img,cx,cy,z,filter){ const s=Math.max(1080/img.width,1920/img.height)*z; c.save(); if(filter) c.filter=filter; c.drawImage(img,540-img.width*s*cx,960-img.height*s*cy,img.width*s,img.height*s); c.restore(); }

// ---------------------------------------------------------------- the stickman
// J: joints in px. r = head radius. face: {eyes:'open'|'half'|'smile'|'side', lx,ly (pupil look -1..1), brow:'worried'|'sad'|'flat', mouth:'frown'|'flat'|'smile'|'o', lid 0..1, rot}
function stick(c,J,face={},o={}){ const r=J.r, lw=o.lw||Math.max(5,r*0.105), ink=o.ink||'#0b0b0d';
  c.save(); c.lineCap='round'; c.lineJoin='round'; c.strokeStyle=ink; c.fillStyle=ink; c.lineWidth=lw;
  const seg=(...p)=>{ c.beginPath(); c.moveTo(...p[0]); for(let i=1;i<p.length;i++) c.lineTo(...p[i]); c.stroke(); };
  const legs=()=>{ if(J.lk){ seg(J.hip,J.lk,J.lf); foot(J.lf,J.lfd||1); } if(J.rk){ seg(J.hip,J.rk,J.rf); foot(J.rf,J.rfd||1); } };
  const foot=(p,d)=>{ c.beginPath(); c.ellipse(p[0]+d*lw*0.9,p[1]+lw*0.2,lw*1.9,lw*0.95,0,0,7); c.fill(); };
  const hand=(p,e)=>{ const a=Math.atan2(p[1]-e[1],p[0]-e[0]); c.save(); c.translate(...p); c.rotate(a); c.beginPath(); c.ellipse(lw*0.5,0,lw*1.55,lw*1.25,0,0,7); c.fill(); c.beginPath(); c.ellipse(lw*0.2,-lw*1.05,lw*0.55,lw*0.95,-0.6,0,7); c.fill(); c.restore(); };
  if(!o.noLegs) legs();
  seg(J.neck,J.hip);
  if(J.le){ seg(J.neck,J.le,J.lh); hand(J.lh,J.le); } if(J.re){ seg(J.neck,J.re,J.rh); hand(J.rh,J.re); }
  head(c,J.head[0],J.head[1],r,face,o);
  c.restore(); }
function head(c,x,y,r,f={},o={}){ c.save(); c.translate(x,y); c.rotate(f.rot||0);
  const sk=o.skin||['#ffffff','#e9e9ea','#b9b9bc'];
  c.fillStyle=rad(c,-r*0.3,-r*0.35,r*1.35,[[0,sk[0]],[0.5,sk[1]],[1,sk[2]]]); c.beginPath(); c.arc(0,0,r,0,7); c.fill();
  if(o.shade){ c.save(); c.beginPath(); c.arc(0,0,r,0,7); c.clip(); c.fillStyle=o.shade; c.fillRect(-r,-r,2*r,2*r); c.restore(); }
  if(o.hair) o.hair(c,r);
  c.lineWidth=Math.max(4,r*0.075); c.strokeStyle='#0b0b0d'; c.beginPath(); c.arc(0,0,r,0,7); c.stroke();
  face(c,r,f); c.restore(); }
function face(c,r,f){ const ink='#0b0b0d', fx=(f.fx||0)*r, fy=(f.fy||0)*r, sp=r*0.36, er=r*0.27, ey=-r*0.05+fy, kind=f.eyes||'open';
  c.lineCap='round'; c.strokeStyle=ink; c.fillStyle=ink;
  for(const s of (f.one?[f.one]:[-1,1])){ const ex=fx+s*sp*(f.squeeze||1);
    if(kind==='smile'){ c.lineWidth=r*0.06; c.beginPath(); c.arc(ex,ey+er*0.35,er*0.75,Math.PI*1.15,Math.PI*1.85); c.stroke(); continue; }
    if(kind==='closed'){ c.lineWidth=r*0.06; c.beginPath(); c.arc(ex,ey-er*0.2,er*0.75,Math.PI*0.15,Math.PI*0.85); c.stroke(); continue; }
    c.fillStyle='#fff'; c.beginPath(); c.ellipse(ex,ey,er*0.92,er,0,0,7); c.fill(); c.lineWidth=r*0.045; c.stroke();
    const px=ex+(f.lx||0)*er*0.42, py=ey+(f.ly||0)*er*0.42, pr=er*0.62; c.fillStyle=ink; c.beginPath(); c.arc(px,py,pr,0,7); c.fill();
    c.fillStyle='#fff'; c.beginPath(); c.arc(px-pr*0.35,py-pr*0.4,pr*0.32,0,7); c.fill(); c.beginPath(); c.arc(px+pr*0.35,py+pr*0.35,pr*0.14,0,7); c.fill();
    const lid=clamp((f.lid||0)+(kind==='half'?0.45:0));
    if(lid>0){ c.save(); c.beginPath(); c.ellipse(ex,ey,er*0.94,er*1.02,0,0,7); c.clip(); c.fillStyle=f.lidCol||'#e4e4e6'; c.fillRect(ex-er,ey-er,2*er,2*er*lid); c.restore();
      c.lineWidth=r*0.05; c.beginPath(); c.moveTo(ex-er*0.95,ey-er+2*er*lid-(lid>0.9?0:0)); c.quadraticCurveTo(ex,ey-er+2*er*lid+er*0.12,ex+er*0.95,ey-er+2*er*lid); c.stroke();
      c.lineWidth=r*0.045; c.beginPath(); c.ellipse(ex,ey,er*0.92,er,0,0,7); c.stroke(); } }
  // brows
  const b=f.brow||'flat', by=ey-er*1.45; c.lineWidth=r*0.055;
  for(const s of (f.one?[f.one]:[-1,1])){ const ex=fx+s*sp*(f.squeeze||1); let inner=0, outer=0;
    if(b==='worried'){ inner=-er*0.5; outer=er*0.15; } else if(b==='sad'){ inner=-er*0.3; outer=er*0.25; } else if(b==='angry'){ inner=er*0.35; outer=-er*0.2; }
    c.beginPath(); c.moveTo(ex+s*er*0.95,by+outer); c.quadraticCurveTo(ex,by-er*0.1+(inner+outer)/2,ex-s*er*0.7,by+inner); c.stroke(); }
  // mouth
  const my=r*0.5+fy, mw=r*0.2, m=f.mouth||'flat'; c.lineWidth=r*0.05;
  if(m==='frown'){ c.beginPath(); c.moveTo(fx-mw,my+r*0.05); c.quadraticCurveTo(fx,my-r*0.1,fx+mw,my+r*0.05); c.stroke(); }
  else if(m==='smile'){ c.beginPath(); c.moveTo(fx-mw*1.2,my-r*0.04); c.quadraticCurveTo(fx,my+r*0.14,fx+mw*1.2,my-r*0.04); c.stroke(); }
  else if(m==='o'){ c.beginPath(); c.ellipse(fx,my,r*0.06,r*0.08,0,0,7); c.stroke(); }
  else { c.beginPath(); c.moveTo(fx-mw*0.8,my); c.quadraticCurveTo(fx,my-r*0.03,fx+mw*0.8,my+r*0.01); c.stroke(); } }
const blinkAt=(t,list)=>list.reduce((a,b)=>Math.max(a,1-Math.abs(t-b)/0.075),0);
const breathe=(t,a=1)=>Math.sin(t*2*Math.PI/3.4)*a;

// ---------------------------------------------------------------- shot backgrounds (built once)
let N1, N2, N3;
function build(){ N1=noiseCanvas(540,960,120,5,3); N2=noiseCanvas(1080,700,260,5,9); N3=noiseCanvas(540,960,40,4,21); }

// ---------------------------------------------------------------- shots
function shot1(t){ // spotlight, dark concrete studio, small worried stickman looking up. 0-1.75
  const pu=(u=>u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2)(clamp(t/1.7)), z=1+0.85*pu, cy=lerp(1150,920,pu), sk=(1-pu*0.5)*3;
  g.save(); g.translate(540+Math.sin(t*9.3)*sk,lerp(1150,760,pu)+Math.sin(t*7.1)*sk); g.scale(z,z); g.translate(-540,-cy);
  const fk=0.82+0.18*Math.sin(t*31)*Math.sin(t*12.7)-(t>0.45&&t<0.52?0.45:0)-(t>0.58&&t<0.62?0.3:0);
  g.fillStyle='#141416'; g.fillRect(-200,-200,1480,2320);
  g.globalAlpha=0.16; g.drawImage(N1,-200,-200,1480,1500); g.globalAlpha=1;
  const wl=g.createLinearGradient(0,0,0,1300); wl.addColorStop(0,'rgba(10,10,12,0.6)'); wl.addColorStop(1,'rgba(10,10,12,0.1)'); g.fillStyle=wl; g.fillRect(-200,-200,1480,1500);
  // floor
  const fl=g.createLinearGradient(0,1200,0,2100); fl.addColorStop(0,'#232326'); fl.addColorStop(1,'#0d0d0f'); g.fillStyle=fl; g.fillRect(-200,1230,1480,900);
  g.save(); g.globalAlpha=0.22; g.globalCompositeOperation='multiply'; g.drawImage(N3,-200,1230,1480,900); g.restore();
  g.fillStyle=rad(g,540,1420,560,[[0,'rgba(200,200,205,0.55)'],[0.5,'rgba(150,150,158,0.2)'],[1,'rgba(0,0,0,0)']]); g.save(); g.translate(540,1420); g.scale(1,0.32); g.translate(-540,-1420); g.fillRect(-100,800,1280,1300); g.restore();
  // light cone
  g.save(); g.globalCompositeOperation='lighter'; const cg=g.createLinearGradient(0,-100,0,1450); cg.addColorStop(0,`rgba(220,220,230,${0.42*fk})`); cg.addColorStop(1,`rgba(220,220,230,${0.05*fk})`); g.fillStyle=cg;
  g.beginPath(); g.moveTo(470,-120); g.lineTo(610,-120); g.lineTo(860,1420); g.lineTo(220,1420); g.closePath(); g.filter='blur(30px)'; g.fill(); g.filter='none'; g.restore();
  glow(g,540,-40,260,'235,235,245',0.7*fk);
  // dust in the beam
  const R=rng(5); g.save(); g.globalCompositeOperation='lighter'; for(let i=0;i<70;i++){ const x0=R()*600+240, y0=R()*1400, sp=10+R()*25; const y=(y0+t*sp)%1400, x=x0+Math.sin(t*0.8+i)*12; const inb=Math.abs(x-540)<(70+y*0.2); if(!inb) continue; g.fillStyle=`rgba(255,255,255,${0.15+R()*0.35})`; g.beginPath(); g.arc(x,y,1.2+R()*2.2,0,7); g.fill(); } g.restore();
  // figure: standing, looking up at the light
  const b=breathe(t,4), hx=540+Math.sin(t*1.6)*5, hy=920+b*0.4, r=88;
  const J={ r, head:[hx,hy], neck:[hx,hy+r], hip:[hx,hy+r+215+b*0.2], le:[hx-38,hy+r+120], lh:[hx-30,hy+r+215], re:[hx+38,hy+r+120], rh:[hx+30,hy+r+215], lk:[hx-24,hy+r+330], lf:[hx-38,hy+r+440], rk:[hx+24,hy+r+330], rf:[hx+38,hy+r+440], lfd:-1, rfd:1 };
  // reflection + contact shadow
  g.save(); g.globalAlpha=0.15; g.translate(0,2*(hy+r+455)); g.scale(1,-1); g.filter='blur(4px)'; stick(g,J,{eyes:'open',ly:-1,brow:'worried',mouth:'frown'}); g.restore();
  g.fillStyle=rad(g,540,hy+r+455,130,[[0,'rgba(0,0,0,0.55)'],[1,'rgba(0,0,0,0)']]); g.save(); g.translate(540,hy+r+455); g.scale(1,0.18); g.beginPath(); g.arc(0,0,130,0,7); g.fill(); g.restore();
  const dn=sm((t-1.0)/0.25); stick(g,J,{eyes:'open',lx:Math.sin(t*2.7)*0.3*(1-dn),ly:lerp(-0.95,0.05,dn),brow:dn>0.5?'sad':'worried',mouth:'frown',lid:dn*0.18+blinkAt(t,[0.62]),rot:Math.sin(t*1.4)*0.04*(1-dn)});
  g.restore();
  }

// his own silhouette (one colour), used for the cast shadow
function sil(c,J,lw,fist=1){ c.lineCap='round'; c.lineJoin='round'; c.lineWidth=lw; const seg=(...p)=>{ c.beginPath(); c.moveTo(...p[0]); for(let i=1;i<p.length;i++) c.lineTo(...p[i]); c.stroke(); };
  seg(J.neck,J.hip); seg(J.neck,J.le,J.lh); seg(J.neck,J.re,J.rh); seg(J.hip,J.lk,J.lf); seg(J.hip,J.rk,J.rf);
  c.beginPath(); c.arc(J.head[0],J.head[1],J.r,0,7); c.fill(); for(const h of [J.lh,J.rh]){ c.beginPath(); c.arc(h[0],h[1],lw*1.5*fist,0,7); c.fill(); }
  for(const f of [J.lf,J.rf]){ c.beginPath(); c.ellipse(f[0],f[1],lw*1.9,lw*0.9,0,0,7); c.fill(); } }
function walkPose(cx,fy,r,ph){ const L=Math.max(0,Math.sin(ph)), Rr=Math.max(0,-Math.sin(ph)), bob=-Math.abs(Math.sin(ph))*r*0.12, n=fy-r*5.05+bob, hy=n-r, sw=Math.sin(ph)*r*0.32;
  return { r, head:[cx,hy], neck:[cx,n], hip:[cx,n+r*2.45], le:[cx-r*0.5,n+r*1.3+sw*0.4], lh:[cx-r*0.42,n+r*2.4+sw], re:[cx+r*0.5,n+r*1.3-sw*0.4], rh:[cx+r*0.42,n+r*2.4-sw],
    lk:[cx-r*0.3,n+r*3.75-L*r*0.45], lf:[cx-r*0.42,fy-L*r*0.55], rk:[cx+r*0.3,n+r*3.75-Rr*r*0.45], rf:[cx+r*0.42,fy-Rr*r*0.55], lfd:-1, rfd:1 }; }
function shot2(t){ // alley: he walks toward us; his shadow on the wall walks with him, then wakes up on ANGER. ref clock 1.75-3.75
  const w=clamp((t-1.75)/2), z=1.0+0.16*sm(w), ang=sm((t-2.52)/0.3);
  g.save(); g.translate(540,1150); g.scale(z,z); g.translate(-540,-1150+Math.sin(t*7)*2);
  if(IMG.alley){ g.save(); g.translate(1080,0); g.scale(-1,1); cover(g,IMG.alley,0.5,0.5,1.04,'grayscale(0.85) contrast(1.15) brightness(0.8)'); g.restore(); } else { g.fillStyle='#1b1c1f'; g.fillRect(0,0,1080,1920); }
  g.fillStyle='rgba(20,26,34,0.3)'; g.fillRect(-100,-100,1280,2120);
  // the right wall catches a low lamp from the front-left: a pale lit panel for the shadow to land on
  g.save(); g.beginPath(); g.moveTo(560,-100); g.lineTo(1200,-100); g.lineTo(1200,2000); g.lineTo(700,1560); g.closePath(); g.clip();
  g.fillStyle='rgba(120,128,140,0.35)'; g.fillRect(500,-100,800,2100); g.globalAlpha=0.35; g.globalCompositeOperation='multiply'; g.drawImage(N3,500,-100,800,2100); g.globalCompositeOperation='source-over'; g.globalAlpha=1;
  g.fillStyle=rad(g,760,1050,700,[[0,'rgba(210,218,232,0.35)'],[1,'rgba(0,0,0,0)']]); g.fillRect(500,-100,800,2100);
  // the man and his pose this frame
  const ph=(t-1.75)*2*Math.PI*0.95, fy=lerp(1360,1760,sm(w)), sc=lerp(0.62,1.2,w), r=95*sc, hx=lerp(470,420,w);
  const J=walkPose(hx,fy,r,ph);
  // cast shadow = his exact pose, projected up the wall, growing as he nears the lamp
  const k=lerp(2.35,1.95,w), ax=hx+150, ay=fy-6;
  g.save(); g.translate(ax,ay); g.transform(1,0,-0.22,1,0,0); g.scale(k*0.92,k); g.translate(-hx,-fy);
  const JS=JSON.parse(JSON.stringify(J)); if(ang>0){ JS.head[0]+=ang*r*0.25; JS.head[1]+=ang*r*0.1; JS.lh[1]-=ang*r*0.2; JS.rh[1]-=ang*r*0.2; JS.le[0]-=ang*r*0.25; JS.re[0]+=ang*r*0.25; }
  g.filter='blur(4px)'; g.fillStyle=g.strokeStyle='rgba(4,5,8,0.9)'; sil(g,JS,r*0.16,1+ang*0.5); g.filter='none';
  // the shadow's face: nothing, until ANGER - then two red slits and a scowl
  if(ang>0){ const [sx,sy]=JS.head, er=r, gl=ang*(0.85+0.15*Math.sin(t*11));
    g.save(); g.shadowColor=`rgba(255,30,20,${gl})`; g.shadowBlur=18; g.fillStyle=`rgba(255,${50-20*gl|0},30,${gl})`;
    for(const s_ of [-1,1]){ g.beginPath(); g.moveTo(sx+s_*er*0.12,sy-er*0.05); g.lineTo(sx+s_*er*0.62,sy-er*0.32); g.lineTo(sx+s_*er*0.55,sy+er*0.08); g.closePath(); g.fill(); }
    g.restore(); g.strokeStyle=`rgba(90,90,100,${0.7*ang})`; g.lineWidth=er*0.07; g.lineCap='round'; g.beginPath(); g.moveTo(sx-er*0.3,sy+er*0.5); g.quadraticCurveTo(sx,sy+er*0.36,sx+er*0.3,sy+er*0.5); g.stroke(); }
  g.restore(); g.restore();
  // lamp spill from the front-left, wet floor glints
  glow(g,80,1350,520,'215,225,245',0.22); g.save(); g.globalCompositeOperation='lighter'; for(let i=0;i<14;i++){ const R0=rng(40+i); const x=R0()*1080, y=1450+R0()*450; g.fillStyle=`rgba(200,210,230,${0.08+0.06*Math.sin(t*3+i)})`; g.fillRect(x,y,60+R0()*120,3); } g.restore();
  // fluorescent flicker
  const fk=0.75+0.25*Math.sin(t*37)*Math.sin(t*13.3)+(Math.sin(t*91)>0.97?-0.4:0); glow(g,560,520,300,'225,235,255',0.3*fk);
  // drizzle
  const R=rng(8); g.strokeStyle='rgba(210,220,235,0.18)'; g.lineWidth=2; for(let i=0;i<90;i++){ const x=R()*1200-60, y=((R()*1920+t*1500)%2000)-40; g.beginPath(); g.moveTo(x,y); g.lineTo(x-6,y+40); g.stroke(); }
  // him: contact shadow, wet reflection, rim glow so the black limbs read, then the figure
  g.fillStyle=rad(g,hx,fy+12,160*sc,[[0,'rgba(0,0,0,0.6)'],[1,'rgba(0,0,0,0)']]); g.save(); g.translate(hx,fy+12); g.scale(1,0.2); g.beginPath(); g.arc(0,0,160*sc,0,7); g.fill(); g.restore();
  g.save(); g.globalAlpha=0.16; g.translate(0,2*(fy+14)); g.scale(1,-1); g.filter='blur(5px)'; stick(g,J,{}); g.restore();
  g.save(); g.filter='blur(6px)'; stick(g,J,{},{lw:r*0.105*2.2,ink:'rgba(170,182,205,0.45)'}); g.restore();
  stick(g,J,{eyes:'half',lx:0,ly:0.05,brow:ang>0.5?'flat':'sad',mouth:'frown',lid:0.15+0.1*ang+blinkAt(t,[2.15]),rot:Math.sin(ph)*0.03},{skin:['#f4f4f6','#d7d8dc','#9c9ea4']});
  // "grows within": red pulse on him
  if(t>3.45){ const a=Math.sin(clamp((t-3.45)/0.3)*Math.PI)*0.5; g.save(); g.globalCompositeOperation='lighter'; glow(g,hx,J.head[1],260,'255,90,40',a); g.restore(); }
  g.restore(); }

function crack(c,x0,y0,len,seed,w){ const R=rng(seed); c.beginPath(); c.moveTo(x0,y0); let x=x0,y=y0,a=R()*0.4-0.2; for(let i=0;i<14;i++){ a+=R()*0.7-0.35; x+=Math.cos(a)*len/14; y+=Math.sin(a)*len/40; c.lineTo(x,y); } c.lineWidth=w; c.stroke(); }
function shot3(t){ // golden-hour park, kneeling, touching a sapling in cracked pavement. 3.75-6.75
  const u=(t-3.75)/3, z=1.0+0.16*sm(u);
  g.save(); g.translate(700,1000); g.scale(z,z); g.translate(-700,-1000);
  if(IMG.park) cover(g,IMG.park,0.42,0.5,1.12,'blur(7px) sepia(0.45) saturate(1.3) brightness(0.8) contrast(1.1)'); else { g.fillStyle='#5a4020'; g.fillRect(0,0,1080,1920); }
  g.fillStyle='rgba(60,36,10,0.25)'; g.fillRect(-200,-200,1480,2320);
  glow(g,880,420,700,'255,200,120',0.55); glow(g,880,420,180,'255,240,210',0.8);
  // god rays
  g.save(); g.globalCompositeOperation='lighter'; for(let i=0;i<6;i++){ const a=2.0+i*0.16+Math.sin(t*0.3+i)*0.01; g.fillStyle=`rgba(255,210,140,${0.05+0.02*Math.sin(t+i)})`; g.beginPath(); g.moveTo(880,420); g.lineTo(880+Math.cos(a)*2200,420+Math.sin(a)*2200); g.lineTo(880+Math.cos(a+0.06)*2200,420+Math.sin(a+0.06)*2200); g.closePath(); g.fill(); } g.restore();
  // pavement slab (foreground, sharp)
  const pv=g.createLinearGradient(0,1080,0,1920); pv.addColorStop(0,'#8a6a48'); pv.addColorStop(0.5,'#5e4630'); pv.addColorStop(1,'#2d2117'); g.fillStyle=pv;
  g.beginPath(); g.moveTo(-200,1120); g.quadraticCurveTo(540,1060,1300,1100); g.lineTo(1300,2200); g.lineTo(-200,2200); g.closePath(); g.fill();
  g.save(); g.globalAlpha=0.35; g.globalCompositeOperation='multiply'; g.drawImage(N3,-200,1060,1500,1100); g.restore();
  g.fillStyle=rad(g,820,1180,600,[[0,'rgba(255,200,130,0.45)'],[1,'rgba(255,200,130,0)']]); g.fillRect(-200,1060,1500,1100);
  g.strokeStyle='rgba(30,20,12,0.85)'; crack(g,-100,1330,900,3,7); crack(g,450,1560,900,9,6); crack(g,900,1240,500,4,5); g.strokeStyle='rgba(255,220,170,0.25)'; crack(g,-100,1336,900,3,2);
  // sapling + white flower in the crack
  const px=905, py=1290, sw=Math.sin(t*2.1)*0.04;
  g.save(); g.translate(px,py); g.rotate(sw); g.strokeStyle='#6c8a2c'; g.lineWidth=7; g.lineCap='round'; g.beginPath(); g.moveTo(0,0); g.quadraticCurveTo(-6,-70,4,-150); g.stroke();
  for(const [y,s,l] of [[-40,-1,70],[-75,1,80],[-110,-1,60],[-30,1,55]]){ g.save(); g.translate(0,y); g.rotate(s*(0.9+Math.sin(t*2+y)*0.05)); g.fillStyle='#8fbf3a'; g.beginPath(); g.ellipse(0,-l/2,l*0.22,l/2,0,0,7); g.fill(); g.strokeStyle='rgba(60,80,20,0.6)'; g.lineWidth=2; g.beginPath(); g.moveTo(0,0); g.lineTo(0,-l); g.stroke(); g.restore(); }
  g.translate(4,-155); for(let i=0;i<6;i++){ g.save(); g.rotate(i*Math.PI/3+t*0.1); g.fillStyle='#fbfbf6'; g.beginPath(); g.ellipse(0,-16,8,15,0,0,7); g.fill(); g.restore(); } g.fillStyle='#f2c230'; g.beginPath(); g.arc(0,0,7,0,7); g.fill();
  g.restore(); glow(g,px,py-150,120,'255,240,200',0.35);
  // kneeling stickman, big close-up, gentle content smile
  const b=breathe(t,4), reach=sm((t-3.9)/1.2), r=205;
  const hx=560+reach*10, hy=700+b*0.5;
  const J={ r, head:[hx,hy], neck:[hx-80,hy+r-10], hip:[330,1090], re:[hx+120,hy+r+150], rh:[lerp(780,880,reach),lerp(1150,1240,reach)], le:[hx-150,hy+r+170], lh:[400,1305],
    lk:[290,1310], lf:[110,1320], rk:[520,1170], rf:[470,1335], lfd:-1, rfd:1 };
  stick(g,J,{eyes:t<4.6?'half':'closed',lx:0.4,ly:0.9,brow:'sad',mouth:'smile',rot:0.22+Math.sin(t*0.9)*0.015,lid:0.2},{lw:20,skin:['#ffffff','#f3ece0','#b8a990']});
  // falling leaves
  const R=rng(12); for(let i=0;i<9;i++){ const x0=R()*1080, sp=60+R()*80, ph=R()*10; const y=((t*sp+R()*1500)%1700)-200, x=x0+Math.sin(t*1.5+ph)*60;
    g.save(); g.translate(x,y); g.rotate(t*2+ph); g.fillStyle=i%3?'#b6d23a':'#e0c040'; g.beginPath(); g.ellipse(0,0,9,20,0,0,7); g.fill(); g.restore(); }
  g.restore(); }

function shot4(t){ // dark office, alone at the end of the table, others whispering. 6.75-9.5
  const u=(t-6.75)/2.75, z=1.0+0.04*sm(u)+0.5*sm((t-7.8)/1.3);
  g.save(); g.translate(545,700); g.scale(z,z); g.translate(-545,-700);
  g.fillStyle='#0c0e12'; g.fillRect(-100,-100,1280,2120);
  // window wall with night city
  const wy0=260, wy1=760; const wg=g.createLinearGradient(0,wy0,0,wy1); wg.addColorStop(0,'#0f141d'); wg.addColorStop(1,'#1a2230'); g.fillStyle=wg; g.fillRect(-100,wy0,1280,wy1-wy0);
  const R=rng(31); for(let i=0;i<420;i++){ const x=R()*1280-100, y=wy0+120+Math.pow(R(),0.7)*(wy1-wy0-120), s=1+R()*3, tw=0.6+0.4*Math.sin(t*3+i);
    g.fillStyle=R()<0.75?`rgba(235,225,200,${0.35*tw})`:`rgba(150,190,255,${0.3*tw})`; g.fillRect(x,y,s,s); }
  for(let i=0;i<14;i++){ const bx=R()*1280-100, bw=40+R()*120, bh=80+R()*260; g.fillStyle='rgba(8,10,14,0.55)'; g.fillRect(bx,wy1-bh,bw,bh); }
  g.fillStyle='rgba(12,14,18,0.95)'; for(let x=-100;x<1280;x+=230) g.fillRect(x,wy0,14,wy1-wy0); g.fillRect(-100,wy0,1280,12);
  glow(g,540,wy0+40,500,'190,200,220',0.14); for(const x of [300,540,780]) glow(g,x,170,60,'230,235,255',0.5);
  g.fillStyle='#08090c'; g.fillRect(-100,wy1,1280,120);
  // table in perspective
  const tg=g.createLinearGradient(0,800,0,1500); tg.addColorStop(0,'#2a2e36'); tg.addColorStop(1,'#101216'); g.fillStyle=tg;
  g.beginPath(); g.moveTo(330,830); g.lineTo(750,830); g.lineTo(1250,1560); g.lineTo(-170,1560); g.closePath(); g.fill();
  g.fillStyle=rad(g,560,900,420,[[0,'rgba(200,210,230,0.18)'],[1,'rgba(0,0,0,0)']]); g.fill();
  g.fillStyle='rgba(120,130,150,0.25)'; g.fillRect(500,1010,70,24);                 // small device on table
  // our guy, small, alone at the far end (only upper body above the table)
  const b=breathe(t,2); const hx=545, hy=670+b*0.3, r=52;
  g.save(); g.lineCap='round'; g.strokeStyle='#0b0b0d'; g.lineWidth=7; g.beginPath(); g.moveTo(hx,hy+r); g.lineTo(hx,830); g.stroke(); g.restore();
  g.fillStyle='#16181d'; g.fillRect(hx-60,700,120,130);                               // his chair back
  stick(g,{r,head:[hx,hy],neck:[hx,hy+r],hip:[hx,830]},{eyes:'open',lx:0,ly:0.85,brow:'sad',mouth:'flat',lid:0.25+blinkAt(t,[7.2,8.9])},{lw:7});
  // whispering pairs at the sides (black hair), glancing at him
  const pair=(x,dir,ph)=>{ for(const k of [0,1]){ const px=x+k*dir*-92, py=700+Math.sin(t*(t<7.73?9:2)+ph+k)*(t<7.73?5:2), rr=64, hair=(c,r)=>{ c.fillStyle='#0b0b0d'; c.beginPath(); c.arc(0,-r*0.15,r*1.02,Math.PI*1.05,Math.PI*1.95); c.quadraticCurveTo(r*0.4,-r*0.55,-r*0.95,-r*0.35); c.fill(); };
      g.save(); g.lineCap='round'; g.strokeStyle='#0b0b0d'; g.lineWidth=7; g.beginPath(); g.moveTo(px,py+rr); g.lineTo(px+dir*-6,830); g.stroke(); g.restore();
      const lk=sm((t-7.73)/0.12), talk=1-lk, mo=talk>0.5&&Math.sin(t*15+k*2.1+ph*3)>0.1;
      head(g,px,py,rr,{eyes:'open',lx:lerp(k?dir:-dir,-dir,lk)*0.9,ly:0.1,brow:lk>0.5?'flat':'flat',mouth:mo?'o':'flat',rot:lerp((k?1:-1)*dir*0.18,-dir*0.12,lk),squeeze:0.9},{hair}); } };
  pair(150,-1,0); pair(930,1,1.3);
  // foreground silhouette: someone's head + chair back, lower left
  g.save(); g.filter='blur(3px)'; g.fillStyle='#060708'; g.beginPath(); g.ellipse(220,1300,190,205,0,0,7); g.fill(); g.fillRect(40,1460,420,700);
  g.strokeStyle='rgba(120,130,150,0.25)'; g.lineWidth=6; g.beginPath(); g.ellipse(220,1300,190,205,0,-1.2,0.2); g.stroke(); g.restore();
  g.fillStyle='#0a0b0d'; g.fillRect(700,1500,600,700); g.fillStyle='rgba(120,125,140,0.12)'; g.fillRect(700,1500,600,10);
  g.restore(); }

function shot5(t){ // rainy cafe window, he reaches out, she looks down. 9.5-10.75
  const u=(t-9.5)/1.25, z=1.04+0.05*sm(u);
  g.save(); g.translate(540,1100); g.scale(z,z); g.translate(-540,-1100);
  g.fillStyle='#120c0a'; g.fillRect(-100,-100,1280,2120);
  // city bokeh through the window
  const R=rng(44); for(let i=0;i<70;i++){ const x=R()*1280-100, y=200+R()*1100, rr=14+R()*46, col=['255,70,50','255,170,80','255,230,190','200,120,60'][i%4]; glow(g,x,y,rr*2,col,0.25+R()*0.35); }
  g.fillStyle='rgba(20,12,10,0.35)'; g.fillRect(-100,-100,1280,2120);
  // drops + streaks on the glass
  for(let i=0;i<160;i++){ const x=R()*1180-50, y0=R()*1500, sp=R()<0.15?200+R()*300:0, y=(y0+t*sp)%1500+100, rr=2+R()*6;
    g.fillStyle='rgba(255,220,190,0.22)'; g.beginPath(); g.arc(x,y,rr,0,7); g.fill(); if(sp){ g.strokeStyle='rgba(255,220,190,0.12)'; g.lineWidth=rr*0.8; g.beginPath(); g.moveTo(x,y); g.lineTo(x+2,y-90); g.stroke(); } }
  // window frame + interior
  g.fillStyle='#1d130e'; g.fillRect(160,0,26,1500); g.fillRect(-100,1420,1280,40);
  glow(g,330,420,160,'255,190,110',0.8); g.fillStyle='#2a1a10'; g.beginPath(); g.moveTo(290,430); g.lineTo(370,430); g.lineTo(350,400); g.lineTo(310,400); g.closePath(); g.fill();
  glow(g,880,520,140,'255,180,100',0.6);
  // table
  g.fillStyle='#3b2416'; g.beginPath(); g.moveTo(140,1380); g.lineTo(940,1380); g.lineTo(990,1440); g.lineTo(100,1440); g.closePath(); g.fill(); g.fillStyle='rgba(255,180,100,0.15)'; g.fillRect(140,1380,800,10);
  g.fillStyle='#24150c'; g.fillRect(500,1440,30,500);
  // cups with steam
  for(const x of [430,560,690]){ g.fillStyle='#e9e2d8'; g.beginPath(); g.ellipse(x,1380,64,14,0,0,7); g.fill(); g.beginPath(); g.moveTo(x-40,1330); g.lineTo(x+40,1330); g.lineTo(x+30,1376); g.lineTo(x-30,1376); g.closePath(); g.fill(); g.fillStyle='#4a2a16'; g.beginPath(); g.ellipse(x,1331,40,9,0,0,7); g.fill();
    g.strokeStyle='#e9e2d8'; g.lineWidth=6; g.beginPath(); g.arc(x+44,1350,13,-1.4,1.4); g.stroke();
    g.save(); g.globalAlpha=0.25; g.strokeStyle='#fff'; g.lineWidth=10; g.lineCap='round'; for(let k=0;k<2;k++){ g.beginPath(); for(let y=0;y<140;y+=10){ const xx=x+Math.sin(y*0.05+t*3+k*2)*10+k*14-7; y?g.lineTo(xx,1320-y):g.moveTo(xx,1320-y); } g.stroke(); } g.restore(); }
  // him (left), reaching across
  const b=breathe(t,3), reach=sm((t-9.55)/0.9), r=120, hx=300, hy=1010+b*0.4;
  const J={ r, head:[hx,hy], neck:[hx+10,hy+r], hip:[hx+10,1530], le:[hx-60,hy+r+170], lh:[hx+20,1370], re:[lerp(hx+110,hx+180,reach),hy+r+150], rh:[lerp(hx+190,hx+330,reach),lerp(1340,1300,reach)],
    lk:[hx+110,1560], lf:[hx+100,1780], rk:[hx+130,1570], rf:[hx+130,1790] };
  stick(g,J,{eyes:'open',lx:0.8,ly:0.2,brow:'worried',mouth:'flat',rot:0.06,lid:0.1+blinkAt(t,[10.4])},{lw:12,skin:['#f6e8da','#e8d2bd','#b99a80']});
  // her (right), long black hair, head down
  const sx=820, sy=1060+b*0.3, sr=112, hair=(c,r)=>{ c.fillStyle='#0b0b0d'; c.beginPath(); c.moveTo(-r*1.05,0); c.quadraticCurveTo(-r*1.15,-r*1.1,0,-r*1.08); c.quadraticCurveTo(r*1.15,-r*1.1,r*1.05,0); c.lineTo(r*1.12,r*1.6); c.lineTo(r*0.55,r*1.5); c.quadraticCurveTo(r*0.6,-r*0.5,-r*0.2,-r*0.55); c.quadraticCurveTo(-r*0.75,-r*0.4,-r*0.8,r*0.2); c.closePath(); c.fill(); };
  stick(g,{ r:sr, head:[sx,sy], neck:[sx-5,sy+sr], hip:[sx+10,1530], le:[sx-70,sy+sr+140], lh:[sx-60,1330], re:[sx+20,sy+sr+160], rh:[sx-40,1340], lk:[sx-80,1570], lf:[sx-80,1790], rk:[sx-50,1575], rf:[sx-40,1790] },
    {eyes:'half',fx:-0.18,lx:-0.3,ly:0.9,brow:'sad',mouth:'frown',rot:-0.12,lid:0.35},{lw:12,hair});
  g.restore(); }

function shot6(t){ // dark bedroom, sitting on the bed edge, phone glowing on the floor. 10.75-13.25
  const u=(t-10.75)/2.5, z=1.03+0.07*sm(u);
  g.save(); g.translate(600,1100); g.scale(z,z); g.translate(-600,-1100);
  const bg=g.createLinearGradient(0,0,0,1920); bg.addColorStop(0,'#0e131c'); bg.addColorStop(1,'#07090d'); g.fillStyle=bg; g.fillRect(-100,-100,1280,2120);
  g.save(); g.globalAlpha=0.12; g.drawImage(N1,-100,-100,1280,1200); g.restore();
  // window top-left with city
  g.fillStyle='#1a2a44'; g.fillRect(-20,60,340,330); const R=rng(61); for(let i=0;i<140;i++){ g.fillStyle=`rgba(255,${200+R()*55|0},${150+R()*80|0},${0.25+R()*0.5})`; g.fillRect(-20+R()*340,200+R()*190,2+R()*3,2+R()*3); }
  g.fillStyle='rgba(120,160,220,0.08)'; g.fillRect(-20,60,340,330); g.strokeStyle='#05070a'; g.lineWidth=16; g.strokeRect(-20,60,340,330);
  g.save(); g.globalCompositeOperation='lighter'; g.fillStyle='rgba(110,140,200,0.06)'; g.beginPath(); g.moveTo(-20,390); g.lineTo(320,390); g.lineTo(700,1500); g.lineTo(100,1500); g.closePath(); g.filter='blur(20px)'; g.fill(); g.filter='none'; g.restore();
  // lamp on a nightstand
  g.fillStyle='#0c0f15'; g.fillRect(520,820,170,210); glow(g,610,700,240,'255,190,120',0.45); g.fillStyle='#3a2a1c'; g.beginPath(); g.moveTo(570,700); g.lineTo(650,700); g.lineTo(670,760); g.lineTo(550,760); g.closePath(); g.fill(); g.fillStyle='#2a1e14'; g.fillRect(605,760,10,60);
  // desk chair silhouette left
  g.fillStyle='#090b10'; g.beginPath(); g.ellipse(160,980,120,170,0,0,7); g.fill(); g.fillRect(140,1140,40,240); g.fillRect(40,1370,240,20);
  // floor
  const fl=g.createLinearGradient(0,1250,0,1920); fl.addColorStop(0,'#141a24'); fl.addColorStop(1,'#07090d'); g.fillStyle=fl; g.fillRect(-100,1250,1280,800);
  // bed on the right
  g.fillStyle='#1c2638'; g.beginPath(); g.moveTo(640,1000); g.lineTo(1250,980); g.lineTo(1250,1820); g.lineTo(700,1820); g.quadraticCurveTo(640,1500,640,1000); g.fill();
  g.strokeStyle='rgba(120,150,200,0.18)'; g.lineWidth=5; for(const [a,b2] of [[700,1150],[760,1400],[900,1250],[1000,1600],[820,1650]]){ g.beginPath(); g.moveTo(a,b2); g.quadraticCurveTo(a+120,b2-60,a+260,b2+30); g.stroke(); }
  g.fillStyle='#24304a'; g.fillRect(820,900,400,110);
  // phone on the floor, screen up, glowing
  const pg=0.85+0.15*Math.sin(t*2); g.save(); g.translate(330,1640); g.rotate(-0.5); g.fillStyle='#0b0d12'; g.fillRect(-48,-26,96,52); g.fillStyle=`rgba(150,190,255,${0.85*pg})`; g.fillRect(-42,-20,84,40); g.restore();
  glow(g,330,1640,260,'120,160,255',0.28*pg);
  // him on the bed edge, head down
  const b=breathe(t,3), hx=720+Math.sin(t*0.6)*3, hy=1030+b*0.6, r=92;
  const J={ r, head:[hx,hy], neck:[hx-6,hy+r], hip:[740,1360], le:[hx-70,hy+r+130], lh:[hx-40,1350], re:[hx+30,hy+r+150], rh:[hx-10,1360], lk:[600,1390], lf:[590,1600], rk:[630,1400], rf:[640,1610], lfd:-1, rfd:-1 };
  stick(g,J,{eyes:'half',lx:-0.6,ly:0.8,brow:'sad',mouth:'flat',rot:-0.32,lid:0.32+blinkAt(t,[12.1]),fx:-0.2,fy:0.12},{lw:11,skin:['#e8eaf0','#c6cad4','#7d8494'],shade:'rgba(40,60,110,0.18)'});
  glow(g,hx-80,hy+40,160,'140,170,255',0.06);
  g.restore();
  if(t>12.85){ g.fillStyle=`rgba(0,0,0,${ramp(t,12.85,13.25)})`; g.fillRect(0,0,1080,1920); } }

function shot7(t){ // rooftop at sunset, phone left on the wet floor. 13.25-16.4
  const u=(t-13.25)/3.15, pu=sm((t-13.4)/2.7), z=1.02+0.85*pu;
  g.save(); g.translate(600,lerp(1050,860,pu)); g.scale(z,z); g.translate(-600,-1050);
  const sk=g.createLinearGradient(0,0,0,1300); sk.addColorStop(0,'#1c2236'); sk.addColorStop(0.45,'#3d4562'); sk.addColorStop(0.75,'#8a6a78'); sk.addColorStop(0.92,'#e09a6a'); sk.addColorStop(1,'#f3c48a'); g.fillStyle=sk; g.fillRect(-100,-100,1280,1420);
  const R=rng(77);
  if(IMG.roof){ const s=2.35, im=IMG.roof; g.save(); g.filter='saturate(0.75) brightness(0.72) contrast(1.1) sepia(0.15)'; g.drawImage(im,540-560*s+t*4,1300-600*s,im.width*s,im.height*s); g.restore();
    const dk=g.createLinearGradient(0,0,0,1340); dk.addColorStop(0,'rgba(15,18,35,0.55)'); dk.addColorStop(0.6,'rgba(40,30,50,0.15)'); dk.addColorStop(1,'rgba(0,0,0,0)'); g.fillStyle=dk; g.fillRect(-100,-100,1280,1440);
    glow(g,860,1230,600,'255,160,90',0.45); glow(g,860,1250,120,'255,235,200',0.8); }
  else { g.save(); g.globalAlpha=0.75; g.globalCompositeOperation='multiply'; g.drawImage(N2,-200+t*6,80,1500,980); g.restore(); glow(g,860,1250,700,'255,170,90',0.55);
    g.fillStyle='#1a1b26'; for(let x=-100;x<1280;){ const bw=30+R()*90, bh=60+Math.pow(R(),2)*420; g.fillRect(x,1300-bh,bw,bh); x+=bw+R()*8; } }
  g.fillStyle='rgba(240,160,110,0.18)'; g.fillRect(-100,1150,1280,160);
  // far roof with tiny people + water tanks (as in the ref)
  g.fillStyle='#14151c'; g.fillRect(-100,1290,600,50); for(const [x,s] of [[30,1],[90,0.9],[140,1.05],[260,0.95],[330,1]]){ g.beginPath(); g.arc(x,1252,14*s,0,7); g.fill(); g.fillRect(x-3,1262,6,30); }
  // birds
  g.strokeStyle='#14151c'; g.lineWidth=3; for(let i=0;i<3;i++){ const bx=(200+i*90+t*40)%1100, by=520+i*40+Math.sin(t*3+i)*6, f=Math.sin(t*12+i)*8; g.beginPath(); g.moveTo(bx-14,by-f); g.lineTo(bx,by); g.lineTo(bx+14,by-f); g.stroke(); }
  // wet roof floor with sky reflection
  const fl=g.createLinearGradient(0,1340,0,1920); fl.addColorStop(0,'#5a4a58'); fl.addColorStop(0.3,'#2a2732'); fl.addColorStop(1,'#111118'); g.fillStyle=fl; g.fillRect(-100,1340,1280,700);
  g.save(); g.globalAlpha=0.35; g.translate(0,2*1340); g.scale(1,-0.6); g.filter='blur(6px)'; g.fillStyle=rad(g,860,1260,600,[[0,'rgba(255,190,120,0.9)'],[1,'rgba(255,190,120,0)']]); g.fillRect(-100,700,1280,800); g.restore();
  g.save(); g.globalAlpha=0.4; g.globalCompositeOperation='multiply'; g.drawImage(N3,-100,1340,1280,700); g.restore();
  // parapet on the right
  g.fillStyle='#24232c'; g.beginPath(); g.moveTo(600,1340); g.lineTo(1280,1300); g.lineTo(1280,1420); g.lineTo(600,1380); g.closePath(); g.fill();
  // puddle sparkle
  for(let i=0;i<20;i++){ const x=R()*1080, y=1400+R()*500; g.fillStyle=`rgba(255,200,150,${0.2*(0.5+0.5*Math.sin(t*4+i))})`; g.fillRect(x,y,30+R()*60,2); }
  // the phone left on the ground, screen lit
  g.save(); g.translate(330,1760); g.rotate(-0.18); g.fillStyle='#16161c'; g.fillRect(-70,-34,140,68); g.fillStyle='rgba(255,200,150,0.75)'; g.fillRect(-62,-26,124,52); g.restore(); glow(g,330,1760,200,'255,190,140',0.35);
  // him, standing, head turned aside, dusk-shaded face
  const b=breathe(t,3), turn=sm((t-14.85)/0.35), hx=600, hy=1050+b*0.4, r=86;
  const J={ r, head:[hx,hy], neck:[hx,hy+r], hip:[hx,hy+r+240], le:[hx-30,hy+r+130], lh:[hx-26,hy+r+240], re:[hx+30,hy+r+130], rh:[hx+26,hy+r+240], lk:[hx-18,hy+r+370], lf:[hx-26,hy+r+500], rk:[hx+16,hy+r+370], rf:[hx+24,hy+r+500], lfd:-1, rfd:1 };
  g.save(); g.globalAlpha=0.25; g.translate(0,2*(hy+r+510)); g.scale(1,-1); g.filter='blur(5px)'; stick(g,J,{}); g.restore();
  stick(g,J,{eyes:'half',fx:lerp(-0.45,0,turn),squeeze:lerp(0.75,1,turn),lx:lerp(-0.9,0,turn),ly:0.05,brow:turn>0.5?'angry':'flat',mouth:'flat',lid:lerp(0.2,0.42,turn),lidCol:'#8a8a96'},{skin:['#c9cad6','#9fa1b0','#5c5e6c'],shade:`rgba(10,12,24,${0.1+0.4*sm((t-13.6)/1.6)})`});
  g.fillStyle=`rgba(5,6,14,${0.35*sm((t-13.5)/1.8)})`; g.fillRect(-200,-200,1480,2320);
  g.restore();
  if(t>16.0){ const a=ramp(t,16.0,16.4); g.save(); g.filter=`blur(${a*14}px)`; g.drawImage(cv,0,0,W,H,0,0,1080,1920); g.restore(); } }

const SHOTS=[[0,1.75,shot1],[1.75,3.75,shot2],[3.75,6.75,shot3],[6.75,9.5,shot4],[9.5,10.75,shot5],[10.75,13.25,shot6],[13.25,16.4,shot7]];   // ref clock
const CUTS=[0,1.9,4.15,7.1,10.05,12.0,15.2,19.0];   // VO clock v2.1 (1.11x + micro-pauses)
const shotAt=t=>{ let i=CUTS.findIndex((c,k)=>t>=c&&t<CUTS[k+1]); if(i<0) i=6; const [o0,o1]=SHOTS[i], n0=CUTS[i], n1=CUTS[i+1]; return [i,o0+(t-n0)*(o1-o0)/(n1-n0)]; };
const DUR=19.0;

// ---------------------------------------------------------------- captions (ref style: condensed caps, white, current word red)
let WORDS=[["PSYCHOLOGY", 0.0], ["SAYS", 0.968], ["/", 1.98], ["THE", 1.98], ["MOST", 2.169], ["DANGEROUS", 2.357], ["/", 2.923], ["ANGER", 2.923], ["/", 3.96], ["GROWS", 3.96], ["WITHIN", 4.174], ["SOMEONE", 4.602], ["/", 5.03], ["WHO", 5.03], ["HAS", 5.244], ["A", 5.458], ["/", 5.672], ["GOOD", 5.672], ["HEART", 5.886], ["/", 7.25], ["BECAUSE", 7.25], ["THEY", 7.701], ["STAY", 7.927], ["/", 8.152], ["SILENT", 8.152], ["FOR", 8.603], ["TOO", 8.829], ["/", 9.054], ["LONG", 9.054], ["/", 10.16], ["FORGIVE", 10.16], ["TOO", 10.725], ["MUCH", 11.007], ["/", 12.12], ["AND", 12.12], ["CARRY", 12.368], ["PAIN", 12.862], ["/", 13.27], ["NOBODY", 13.27], ["NOTICED", 13.864], ["/", 15.31], ["UNTIL", 15.31], ["ONE", 15.775], ["DAY", 16.007], ["/", 17.19], ["THEY", 17.19], ["STOP", 17.455], ["CARING", 17.72]];
function captions(t){ let start=0; for(let i=0;i<WORDS.length;i++){ if(WORDS[i][0]==='/'&&WORDS[i][1]<=t) start=i+1; }
  const line=[]; for(let i=start;i<WORDS.length&&WORDS[i][0]!=='/';i++) line.push(WORDS[i]); if(!line.length||line[0][1]>t+0.001) return;
  let act=0; line.forEach((w,i)=>{ if(w[1]<=t) act=i; });
  g.save(); g.font='76px "Anton"'; g.textBaseline='middle'; const sp=g.measureText(' ').width*0.9, ws=line.map(w=>g.measureText(w[0]).width), tw=ws.reduce((a,b)=>a+b,0)+sp*(line.length-1);
  let x=540-tw/2; const y=1243;
  line.forEach((w,i)=>{ g.lineJoin='round'; g.shadowColor='rgba(0,0,0,0.7)'; g.shadowBlur=10; g.shadowOffsetY=3; g.lineWidth=9; g.strokeStyle='#000'; g.strokeText(w[0],x,y); g.shadowColor='transparent';
    g.fillStyle=i===act?'#e5161a':'#ffffff'; g.fillText(w[0],x,y); x+=ws[i]+sp; });
  g.restore(); }

const GT=mk(W,H), gx=GT.getContext('2d');
function grade(t,si){ g.setTransform(1,0,0,1,0,0); const warm=si===2;
  // crush + cool: darker, more contrast, less colour (the park keeps some warmth)
  gx.clearRect(0,0,W,H); gx.filter=warm?'brightness(0.9) contrast(1.15) saturate(0.9)':'brightness(0.9) contrast(1.22) saturate(0.68)'; gx.drawImage(cv,0,0); gx.filter='none'; g.drawImage(GT,0,0);
  g.save(); g.globalCompositeOperation='soft-light'; g.fillStyle=warm?'rgba(60,90,140,0.18)':'rgba(70,110,170,0.32)'; g.fillRect(0,0,W,H); g.restore();
  // drifting cold haze
  g.save(); g.globalCompositeOperation='screen'; g.globalAlpha=warm?0.03:0.05; g.drawImage(N1,-W*0.2+((t*18)%(W*0.2)),0,W*1.4,H); g.restore();
  // breathing flicker, like an old bulb
  const fl=0.04*Math.max(0,Math.sin(t*23)*Math.sin(t*7.1))+(Math.sin(t*3.3+1)>0.995?0.08:0); if(fl>0){ g.fillStyle=`rgba(0,0,0,${fl})`; g.fillRect(0,0,W,H); }
  const vg=g.createRadialGradient(W/2,H*0.47,W*0.32,W/2,H*0.5,H*0.7); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(2,4,10,0.5)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  const R=rng(Math.floor(t*30)+7), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*10; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0); }

window.renderAt=t=>{ g.setTransform(S,0,0,S,0,0); g.filter='none'; g.globalAlpha=1; g.globalCompositeOperation='source-over';
  const [si,tt]=shotAt(t); SHOTS[si][2](tt);
  grade(t,si); g.setTransform(S,0,0,S,0,0); captions(t); return cv.toDataURL('image/jpeg',0.93); };
window.setWords=w=>{ WORDS=w; };
window.DUR=DUR;
(async()=>{ const f=new FontFace('Anton','url(fonts/Anton-Regular.ttf)'); await f.load(); document.fonts.add(f);
  await Promise.all(['alley','park','roof'].map(loadImg)); build(); window.ready=true; })();
