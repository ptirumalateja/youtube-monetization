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
export { rng, clamp, lerp, sm, out3, back, ramp, K, mk, rad, glow, noiseCanvas, IMG, loadImg, cover, stick, head, face, blinkAt, breathe };
