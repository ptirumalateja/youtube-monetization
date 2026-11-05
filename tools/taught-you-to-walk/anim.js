// He Taught You to Walk: moving hook test (0-4.6 s), 5 Nov 2026.
// Teja: no still frames, everything moves; the pictogram is "good but not a great design"; give people clothes.
// So: clothed flat-illustration stickmen (stick proportions, round heads with a simple side-profile face, hair, glasses),
// soft lamp-side shading, a thin darker edge so overlapping parts separate, and continuous motion in every frame.
// renderAt(t) is pure, so frames can render in any order.
const q=new URLSearchParams(location.search); const W=+q.get('w')||1080, H=+q.get('h')||1920;
const cv=document.createElement('canvas'); cv.width=W; cv.height=H; document.body.appendChild(cv); const g=cv.getContext('2d');
const S=W/1080, FL=1500, WARM='255,184,112', COOL='190,210,255';
const rng=seed=>{ let s=seed>>>0; return ()=>((s=(s*1664525+1013904223)>>>0)/4294967296); };
const clamp=(x,a=0,b=1)=>Math.max(a,Math.min(b,x)), lerp=(a,b,u)=>a+(b-a)*u, sm=u=>{u=clamp(u);return u*u*(3-2*u);};
const ease=u=>{u=clamp(u);return u<0.5?4*u*u*u:1-Math.pow(-2*u+2,3)/2;}, out3=u=>1-Math.pow(1-clamp(u),3);
const ramp=(t,a,b,e=sm)=>e((t-a)/(b-a));
const L2=(A,B,u)=>[lerp(A[0],B[0],u),lerp(A[1],B[1],u)];
// keyframes of points or numbers: [[t,v],...]
function K(keys,t,e=sm){ if(t<=keys[0][0]) return keys[0][1]; for(let i=1;i<keys.length;i++) if(t<=keys[i][0]){ const u=e((t-keys[i-1][0])/(keys[i][0]-keys[i-1][0])); const a=keys[i-1][1], b=keys[i][1]; return Array.isArray(a)?L2(a,b,u):lerp(a,b,u); } return keys[keys.length-1][1]; }
function rr(c,x,y,w,h,r){ c.beginPath(); c.moveTo(x+r,y); c.arcTo(x+w,y,x+w,y+h,r); c.arcTo(x+w,y+h,x,y+h,r); c.arcTo(x,y+h,x,y,r); c.arcTo(x,y,x+w,y,r); c.closePath(); }
function glow(x,y,r,c,a){ g.save(); g.globalCompositeOperation='lighter'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},${a})`); rg.addColorStop(0.4,`rgba(${c},${a*0.35})`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); g.restore(); }
function tint(hex,k){ const h=hex.replace('#',''); const r=parseInt(h.slice(0,2),16), gg=parseInt(h.slice(2,4),16), b=parseInt(h.slice(4,6),16); return `rgb(${Math.min(255,r*k)|0},${Math.min(255,gg*k)|0},${Math.min(255,b*k)|0})`; }

// ---------------------------------------------------------------- room (side-on living room; era 0 = 25 years ago, 1 = now)
function room(era,t){
  let gr=g.createLinearGradient(0,0,0,FL); gr.addColorStop(0,era?'#3d2c24':'#48342a'); gr.addColorStop(1,era?'#5a4231':'#6a4c36'); g.fillStyle=gr; g.fillRect(-200,-200,1480,FL+200);
  // wallpaper stripes, very soft
  g.fillStyle='rgba(255,220,180,0.035)'; for(let x=-200;x<1280;x+=70) g.fillRect(x,0,30,FL);
  glow(960,780,900,WARM,0.22);
  g.fillStyle='#2e221b'; g.fillRect(-200,FL-14,1480,14);
  gr=g.createLinearGradient(0,FL,0,1920); gr.addColorStop(0,'#5a3e2c'); gr.addColorStop(1,'#3c2a1f'); g.fillStyle=gr; g.fillRect(-200,FL,1480,520);
  g.strokeStyle='rgba(20,12,8,0.3)'; g.lineWidth=3; for(let i=0;i<7;i++){ const y=FL+30+i*i*9+i*22; g.beginPath(); g.moveTo(-200,y); g.lineTo(1280,y); g.stroke(); }
  g.fillStyle=era?'#6a3528':'#7a3b2a'; rr(g,120,FL+4,880,24,8); g.fill(); g.fillStyle='rgba(255,210,160,0.16)'; g.fillRect(150,FL+10,820,4);
  // window
  const wx=80,wy=560,ww=360,wh=440; gr=g.createLinearGradient(0,wy,0,wy+wh);
  if(era){ gr.addColorStop(0,'#2f3b66'); gr.addColorStop(1,'#6a4c6e'); } else { gr.addColorStop(0,'#f4b67c'); gr.addColorStop(1,'#e9845a'); }
  g.fillStyle=gr; g.fillRect(wx,wy,ww,wh);
  const R=rng(era?9:4); for(let i=0;i<34;i++){ const x=wx+R()*ww, y=wy+wh*0.55+R()*wh*0.45, r=4+R()*12, tw=0.75+0.25*Math.sin(t*2+i); const c=R()<0.7?WARM:'255,230,200'; const rg=g.createRadialGradient(x,y,0,x,y,r); rg.addColorStop(0,`rgba(${c},${0.7*tw})`); rg.addColorStop(1,`rgba(${c},0)`); g.fillStyle=rg; g.fillRect(x-r,y-r,2*r,2*r); }
  // curtain, swaying a touch
  g.fillStyle=era?'#8a4a3a':'#a8603e'; const sw=Math.sin(t*0.9)*6; g.beginPath(); g.moveTo(wx-30,wy-30); g.lineTo(wx+70,wy-30); g.quadraticCurveTo(wx+50+sw,wy+wh*0.5,wx+80+sw,wy+wh+40); g.lineTo(wx-30,wy+wh+40); g.closePath(); g.fill();
  g.strokeStyle='#2a1d16'; g.lineWidth=16; g.strokeRect(wx,wy,ww,wh); g.lineWidth=8; g.beginPath(); g.moveTo(wx+ww/2,wy); g.lineTo(wx+ww/2,wy+wh); g.stroke();
  g.fillStyle='#2a1d16'; g.fillRect(wx-20,wy+wh+4,ww+40,14); g.fillRect(wx-50,wy-40,ww+100,10);
  glow(wx+ww/2,wy+wh/2,420,era?COOL:WARM,0.1);
  // framed photo (now: the toddler holding dad's fingers)
  g.fillStyle='#2a1d16'; rr(g,560,600,170,210,6); g.fill(); g.fillStyle=era?'#d8b98e':'#c9a27a'; g.fillRect(572,612,146,186);
  if(era){ g.fillStyle='#5a4030'; g.beginPath(); g.arc(625,650,11,0,7); g.fill(); g.fillRect(612,665,26,60); g.fillRect(625,700,40,10); g.beginPath(); g.arc(675,712,8,0,7); g.fill(); g.fillRect(668,722,14,34); g.fillRect(605,725,10,60); g.fillRect(630,725,10,60); }
  // floor lamp
  g.strokeStyle='#241a14'; g.lineWidth=10; g.beginPath(); g.moveTo(960,FL-10); g.lineTo(960,800); g.stroke(); g.fillStyle='#241a14'; g.beginPath(); g.ellipse(960,FL-8,46,10,0,0,7); g.fill();
  g.fillStyle='#f7d9a6'; g.beginPath(); g.moveTo(890,800); g.lineTo(1030,800); g.lineTo(1002,700); g.lineTo(918,700); g.closePath(); g.fill();
  glow(960,780,720,WARM,0.38); glow(960,770,160,WARM,0.55);
  // dust in the lamp light
  const D=rng(31); g.save(); g.globalCompositeOperation='lighter'; for(let i=0;i<60;i++){ const x=700+D()*420+Math.sin(t*0.4+i)*12, y=((D()*900+t*(8+D()*10))%900)+650, a=0.25*(0.5+0.5*Math.sin(t*1.5+i)); g.fillStyle=`rgba(255,220,170,${a})`; g.beginPath(); g.arc(x,y,1.6+D()*1.6,0,7); g.fill(); } g.restore();
}
function armchair(x,f,{h=1270,col='#7b4a34'}={}){ const back=x-f*40, front=x+f*170;
  g.fillStyle='#3a2418'; for(const lx of [back+f*14,front-f*14]) g.fillRect(lx-7,h+70,14,FL-h-70);
  const sg=g.createLinearGradient(0,h,0,h+80); sg.addColorStop(0,tint(col,1.15)); sg.addColorStop(1,tint(col,0.8)); g.fillStyle=sg; rr(g,Math.min(back,front)-10,h,Math.abs(front-back)+20,78,26); g.fill();
  g.fillStyle=tint(col,0.92); rr(g,back-f*40-(f>0?10:40),h-330,50,400,24); g.fill();
  g.fillStyle=tint(col,1.05); rr(g,Math.min(back,front)+(f>0?10:60),h-40,110,34,16); g.fill(); }   // armrest
function blocks(){ [[790,'#d8a34a',0],[842,'#5a8ad8',0],[816,'#d85a4a',1]].forEach(([x,c,up])=>{ g.fillStyle=c; rr(g,x,FL-52-up*54,50,50,6); g.fill(); g.fillStyle='rgba(255,255,255,0.18)'; g.fillRect(x+6,FL-46-up*54,38,6); });
  g.fillStyle='#e9d26a'; g.beginPath(); g.arc(930,FL-28,28,0,7); g.fill(); }
function cane(x,y){ g.strokeStyle='#8a5a36'; g.lineWidth=14; g.lineCap='round'; g.beginPath(); g.moveTo(x,y); g.lineTo(x+40,FL-6); g.stroke(); g.beginPath(); g.arc(x-14,y,14,0,Math.PI*1.1,true); g.stroke(); }

// ---------------------------------------------------------------- clothed character (side view)
function capsule(c,a,b,ra,rb){ const ang=Math.atan2(b[1]-a[1],b[0]-a[0]); c.moveTo(a[0]+Math.cos(ang+Math.PI/2)*ra,a[1]+Math.sin(ang+Math.PI/2)*ra);
  c.arc(a[0],a[1],ra,ang+Math.PI/2,ang+Math.PI*1.5); c.arc(b[0],b[1],rb,ang-Math.PI/2,ang+Math.PI/2); c.closePath(); }
function ik(Sp,T,l1,l2,bend){ const dx=T[0]-Sp[0], dy=T[1]-Sp[1]; const d=Math.max(1,Math.min(Math.hypot(dx,dy),l1+l2-0.5)), base=Math.atan2(dy,dx);
  const a=Math.acos(clamp((l1*l1+d*d-l2*l2)/(2*l1*d),-1,1)); const ang=base+bend*a; return [[Sp[0]+l1*Math.cos(ang),Sp[1]+l1*Math.sin(ang)],[Sp[0]+d*Math.cos(base),Sp[1]+d*Math.sin(base)]]; }
const BODY={
  adult:{torso:210,thigh:172,shin:165,up:128,fore:120,head:54,neck:84,rT:[46,56],rP:[30,25,22],rS:[25,22],rF:[15,13],hand:17,shoe:[40,16]},
  kid:  {torso:96, thigh:64, shin:58, up:52, fore:46, head:42,neck:52,rT:[27,31],rP:[17,15,13],rS:[13,12],rF:[9,8],hand:10,shoe:[20,9]},
};
// outfit: skin, top, pants, shoes, hair, hairStyle ('short'|'grey'|'tuft'), glasses, sleeve ('long'|'short'), cardigan (colour)
function fill(col,a,b){ const gr=g.createLinearGradient(a[0],a[1],b[0],b[1]); gr.addColorStop(0,tint(col,0.82)); gr.addColorStop(1,tint(col,1.1)); return gr; }
function shape(path,col,lit){ g.beginPath(); path(g); g.fillStyle=fill(col,lit[0],lit[1]); g.fill(); g.lineWidth=3; g.strokeStyle=tint(col,0.55); g.stroke(); }
// o: {x,y hip, f, lean, nod, body, fit, legs:{near,far}, arms:{near,far}, face:{eye 0..1 open, brow, mouth}, finger}
function figure(o){ const B=BODY[o.body||'adult'], fc=o.f, hip=[o.x,o.y], F=o.fit;
  const lit=[[o.x-120,o.y],[o.x+160,o.y-200]];                      // the lamp is on the right
  const sh=[hip[0]+fc*Math.sin(o.lean||0)*B.torso, hip[1]-Math.cos(o.lean||0)*B.torso];
  const ha=(o.lean||0)+(o.nod||0); const head=[sh[0]+fc*Math.sin(ha)*B.neck, sh[1]-Math.cos(ha)*B.neck];
  const shA=[sh[0]-fc*8,sh[1]+B.rT[1]*0.5];
  const leg=t=>{ const [k,e]=ik(hip,t,B.thigh,B.shin,-fc); return [hip,k,e]; };
  const arm=t=>{ const [el,e]=ik(shA,t,B.up,B.fore,o.elbow??fc); return [shA,el,e]; };
  const L={near:leg(o.legs.near),far:leg(o.legs.far)}, A={near:arm(o.arms.near),far:arm(o.arms.far)};
  const drawLeg=(P,k)=>{ const pc=k<1?tint(F.pants,k):F.pants, scol=k<1?tint(F.shoes,k):F.shoes, e=P[2];
    if(F.bare){ shape(c=>{ capsule(c,P[0],P[1],B.rP[0],B.rP[1]); },pc,lit); shape(c=>{ capsule(c,P[1],e,B.rF[0]*1.05,B.rF[1]); capsule(c,[e[0]-fc*3,e[1]],[e[0]+fc*B.shoe[0]*0.8,e[1]+2],B.rF[1],B.rF[1]*0.8); },k<1?tint(F.skin,k):F.skin,lit); return; }
    shape(c=>{ capsule(c,P[0],P[1],B.rP[0],B.rP[1]); capsule(c,P[1],e,B.rP[1],B.rP[2]); },pc,lit);
    shape(c=>{ capsule(c,[e[0]-fc*B.shoe[1]*0.6,e[1]+B.shoe[1]*0.3],[e[0]+fc*B.shoe[0],e[1]+B.shoe[1]*0.45],B.shoe[1],B.shoe[1]*0.85); },scol,lit); };
  const drawArm=(P,k)=>{ const top=k<1?tint(F.cardigan||F.top,k):(F.cardigan||F.top), skin=k<1?tint(F.skin,k):F.skin;
    const long=F.sleeve==='long', el=P[1], h=P[2];
    if(long){ shape(c=>{ capsule(c,P[0],el,B.rS[0],B.rS[1]); capsule(c,el,L2(el,h,0.86),B.rS[1],B.rS[1]*0.9); },top,lit); }
    else { shape(c=>{ capsule(c,el,h,B.rF[0],B.rF[1]); },skin,lit); shape(c=>{ capsule(c,P[0],L2(P[0],el,0.6),B.rS[0],B.rS[1]); },top,lit); }
    shape(c=>{ c.moveTo(h[0]+B.hand,h[1]); c.arc(h[0],h[1],B.hand,0,Math.PI*2); },skin,lit); };
  drawLeg(L.far,0.78); drawArm(A.far,0.78); if(o.armsBehind) drawArm(A.near,0.95);
  // torso: top (shirt / hoodie / tee) with a collar, and an open cardigan over it for old dad
  const hipT=[hip[0]-fc*2,hip[1]-B.rT[0]*0.25];
  const torso=c=>{ if(o.hunch){ const mid=[hip[0]+fc*Math.sin((o.lean||0)*0.4)*B.torso*0.55-fc*12,hip[1]-Math.cos((o.lean||0)*0.4)*B.torso*0.55]; capsule(c,hipT,mid,B.rT[0],B.rT[0]*1.12); capsule(c,mid,sh,B.rT[0]*1.12,B.rT[1]); } else capsule(c,hipT,sh,B.rT[0],B.rT[1]); };
  shape(torso,F.cardigan||F.top,lit);
  if(F.cardigan){ g.save(); g.beginPath(); torso(g); g.clip(); g.fillStyle=fill(F.top,lit[0],lit[1]); const fr=[sh[0]+fc*B.rT[1]*0.55,sh[1]]; g.beginPath(); capsule(g,[hip[0]+fc*B.rT[0]*0.7,hip[1]-20],fr,12,22); g.fill(); g.restore(); }
  if(F.hood){ shape(c=>{ c.moveTo(sh[0]-fc*20+30,sh[1]-6); c.arc(sh[0]-fc*20,sh[1]-6,30,0,Math.PI*2); },F.top,lit); }
  // head: skin disc, ear, nose, hair, face
  const r=B.head; shape(c=>{ c.moveTo(head[0]+r,head[1]); c.arc(head[0],head[1],r,0,Math.PI*2); },F.skin,lit);
  g.fillStyle=tint(F.skin,1.0); g.beginPath(); g.arc(head[0]+fc*r*0.92,head[1]+r*0.12,r*0.17,0,7); g.fill();   // nose
  g.fillStyle=tint(F.skin,0.82); g.beginPath(); g.arc(head[0]-fc*r*0.12,head[1]+r*0.08,r*0.18,0,7); g.fill();  // ear
  // hair
  g.fillStyle=F.hair; g.beginPath();
  if(F.hairStyle==='grey'){ g.arc(head[0]-fc*r*0.08,head[1]+r*0.05,r*1.02,Math.PI*(fc>0?0.62:0.38-0.0),Math.PI*(fc>0?1.32:-0.32),fc<0); g.quadraticCurveTo(head[0]-fc*r*0.3,head[1]-r*0.3,head[0]-fc*r*0.55,head[1]+r*0.6); g.fill(); }
  else if(F.hairStyle==='tuft'){ g.arc(head[0]-fc*r*0.05,head[1]-r*0.1,r*1.0,Math.PI*1.05,Math.PI*1.95); g.quadraticCurveTo(head[0]+fc*r*0.2,head[1]-r*0.55,head[0]-fc*r*0.5,head[1]-r*0.45); g.fill();
    g.beginPath(); g.moveTo(head[0],head[1]-r*0.98); g.quadraticCurveTo(head[0]+fc*r*0.3,head[1]-r*1.5,head[0]+fc*r*0.45,head[1]-r*1.2); g.lineWidth=5; g.strokeStyle=F.hair; g.stroke(); }
  else { g.arc(head[0]-fc*r*0.06,head[1]-r*0.02,r*1.05,Math.PI*(fc>0?0.55:0.45),Math.PI*(fc>0?2.05:-1.05),fc<0); g.quadraticCurveTo(head[0]+fc*r*0.5,head[1]-r*0.55,head[0]+fc*r*0.25,head[1]-r*0.35); g.quadraticCurveTo(head[0]-fc*r*0.2,head[1]-r*0.3,head[0]-fc*r*0.5,head[1]+r*0.45); g.fill(); }
  // face: eye (opens / closes), brow, mouth
  const fe=o.face||{}; const ex=head[0]+fc*r*0.5, ey=head[1]-r*0.08, eo=fe.eye??1;
  g.fillStyle='#2a1a14'; g.strokeStyle='#2a1a14'; g.lineCap='round';
  if(eo>0.2){ g.beginPath(); g.ellipse(ex,ey,r*0.09,r*0.13*eo,0,0,7); g.fill(); g.fillStyle='rgba(255,255,255,0.8)'; g.beginPath(); g.arc(ex+fc*r*0.03,ey-r*0.04,r*0.03,0,7); g.fill(); }
  else { g.lineWidth=r*0.06; g.beginPath(); g.arc(ex,ey-r*0.02,r*0.1,0.15*Math.PI,0.85*Math.PI); g.stroke(); }
  const bw=fe.brow??0; g.lineWidth=r*0.07; g.beginPath(); g.moveTo(ex-fc*r*0.14,ey-r*0.26+bw*r*0.06); g.lineTo(ex+fc*r*0.14,ey-r*0.26-bw*r*0.08); g.stroke();
  const mc=fe.mouth??0; g.lineWidth=r*0.06; g.beginPath(); const mx=head[0]+fc*r*0.62, my=head[1]+r*0.42; g.moveTo(mx-fc*r*0.16,my-mc*r*0.04); g.quadraticCurveTo(mx,my+mc*r*0.12,mx+fc*r*0.12,my-mc*r*0.06); g.stroke();
  if(F.glasses){ g.strokeStyle='#3a2a20'; g.lineWidth=4; g.beginPath(); g.arc(ex,ey,r*0.21,0,7); g.stroke(); g.beginPath(); g.moveTo(ex-fc*r*0.21,ey); g.lineTo(head[0]-fc*r*0.05,ey+r*0.02); g.stroke(); }
  drawLeg(L.near,1); if(!o.armsBehind) drawArm(A.near,1);
  if(o.finger){ const h=A.near[2], el=A.near[1]; const d=[h[0]-el[0],h[1]-el[1]], n=Math.hypot(...d); const tip=[h[0]+d[0]/n*30,h[1]+d[1]/n*30]; shape(c=>capsule(c,h,tip,7,6),F.skin,lit); }
  return {hip,sh,head,A,L}; }
const FIT={
  oldDad:{skin:'#c98d64',top:'#e8e2d4',cardigan:'#7a5a3a',pants:'#4a4f5c',shoes:'#3a2a20',hair:'#d6d0c6',hairStyle:'grey',glasses:true,sleeve:'long'},
  dad:   {skin:'#c98d64',top:'#3f6fa8',pants:'#3a3f4a',shoes:'#2a2420',hair:'#1e1714',hairStyle:'short',sleeve:'short'},
  son:   {skin:'#c4875d',top:'#d9603b',pants:'#3d5a80',shoes:'#f0ece4',hair:'#1e1714',hairStyle:'short',sleeve:'long',hood:true},
  kid:   {skin:'#c4875d',top:'#f2c94c',pants:'#5a8ad8',shoes:'#c4875d',hair:'#1e1714',hairStyle:'tuft',sleeve:'short',bare:true},
};

// ---------------------------------------------------------------- props
function phone(x,y,ang,lit=1){ glow(x,y,200,COOL,0.3*lit); g.save(); g.translate(x,y); g.rotate(ang); g.fillStyle='#14161c'; rr(g,-21,-38,42,76,8); g.fill(); g.fillStyle=`rgba(214,228,255,${0.55+0.4*lit})`; rr(g,-17,-33,34,66,5); g.fill();
  g.fillStyle='rgba(60,90,160,0.5)'; for(let i=0;i<3;i++) g.fillRect(-12,-26+i*20,24,12); g.restore(); }
function sigh(x,y,f,a){ if(a<=0) return; g.save(); g.globalAlpha=a; g.strokeStyle='rgba(255,240,220,0.85)'; g.lineWidth=5; g.lineCap='round'; for(let i=0;i<3;i++){ g.beginPath(); g.arc(x+f*(10+i*16),y-6-i*4,12+i*6,-Math.PI*0.35,Math.PI*0.35); g.stroke(); } g.restore(); }
function swoosh(x0,y0,x1,y1,a){ if(a<=0) return; g.save(); g.globalAlpha=a; g.strokeStyle='rgba(255,240,220,0.7)'; g.lineWidth=6; g.lineCap='round'; for(let i=-1;i<=1;i++){ g.beginPath(); g.moveTo(x0,y0+i*18); g.lineTo(x1,y1+i*18); g.stroke(); } g.restore(); }

// ---------------------------------------------------------------- text (drawn unzoomed)
const CREAM='255,244,224', GOLD='255,190,110';
function lines(L,a=1){ if(a<=0) return; g.setTransform(S,0,0,S,0,0);
  const sc=g.createLinearGradient(0,0,0,560); sc.addColorStop(0,`rgba(30,20,14,${0.55*a})`); sc.addColorStop(1,'rgba(30,20,14,0)'); g.fillStyle=sc; g.fillRect(0,0,1080,560);
  g.textBaseline='top'; g.textAlign='center';
  for(const [s,size,col,y] of L){ g.font=`800 ${size}px "Inter"`; g.save(); g.shadowColor='rgba(0,0,0,0.7)'; g.shadowBlur=22; g.shadowOffsetY=4; g.fillStyle=`rgba(${col},${a})`; g.fillText(s,540,y); g.restore(); } }
function counter(label,n,a){ if(a<=0) return; g.setTransform(S,0,0,S,0,0); g.font='800 44px "Inter"'; const s=`${label} ${n}`; const w=g.measureText(s).width+56;
  g.globalAlpha=a; g.fillStyle='rgba(30,20,14,0.65)'; rr(g,540-w/2,1660,w,82,20); g.fill(); g.fillStyle=`rgb(${GOLD})`; g.textAlign='center'; g.textBaseline='middle'; g.fillText(s,540,1703); g.globalAlpha=1; }

// ---------------------------------------------------------------- timeline
const CUT=2.4, DUR=4.6, SEAT=1262;
function camT(c,z,cx,cy){ c.setTransform(S*z,0,0,S*z,S*(540-z*cx),S*(1180-z*cy)); }
function now(t){
  camT(g,K([[0,1.42],[CUT,1.5]],t,x=>x),K([[0,560],[CUT,570]],t),1215); room(1,t); armchair(380,1); armchair(850,-1,{col:'#5a4a3e'}); cane(250,1120);
  const br=Math.sin(t*2.4)*3;                                                    // breathing
  // son: leans in, snatches (0.42-0.56), yanks back, rolls his head with a sigh
  const sonHand=K([[0,[728,1236]],[0.3,[700,1200]],[0.45,[598,1146]],[0.6,[742,1160]],[2.4,[748,1168]]],t,ease);
  const sonLean=K([[0,0.08],[0.42,0.3],[0.62,-0.14],[2.4,-0.12]],t), sonNod=K([[0,0],[0.6,0],[0.95,-0.38],[1.7,-0.3],[2.4,-0.32]],t);
  // dad: two slow taps, the phone is gone, his finger hovers, then the hand sinks and the head drops
  const tap=Math.max(0,Math.sin(clamp(t/0.42)*Math.PI*2))*10*(t<0.42?1:0);
  const dadHand=K([[0,[586,1146]],[0.5,[588,1146]],[1.25,[590,1144]],[2.2,[560,1206]]],t);
  const dadNod=K([[0,0.36],[0.5,0.3],[0.9,0.16],[1.4,0.18],[2.3,0.44]],t);
  const dadFace={eye:1,brow:K([[0,-0.2],[0.8,-0.5],[1.6,-0.6]],t),mouth:K([[0,0.2],[0.8,-0.1],[1.6,-0.5]],t)};
  const sonFace={eye:t>0.75&&t<1.45?0:1,brow:-0.5,mouth:-0.4};
  const D=figure({x:380,y:SEAT+br*0.4,f:1,lean:0.42,nod:dadNod,hunch:1,body:'adult',fit:FIT.oldDad,legs:{near:[575,FL-22],far:[548,FL-22]},arms:{near:[dadHand[0],dadHand[1]+tap],far:[522,1212]},finger:true,face:dadFace});
  const Sn=figure({x:850,y:SEAT+br*0.3,f:-1,lean:sonLean,nod:sonNod,body:'adult',fit:FIT.son,legs:{near:[655,FL-22],far:[684,FL-22]},arms:{near:sonHand,far:[762,1226]},face:sonFace});
  const inDad=t<0.47; const ph=inDad?[dadHand[0]+10,dadHand[1]+28+tap]:[sonHand[0],sonHand[1]-8];
  phone(ph[0],ph[1],inDad?0.25:-0.45,1);
  swoosh(610,1150,720,1160,t>0.45&&t<0.75?1-ramp(t,0.55,0.75):0);
  sigh(Sn.head[0]-50,Sn.head[1]-10,-1,ramp(t,0.75,0.9)*(1-ramp(t,1.7,2.1)));
  lines([['HE TAUGHT YOU',92,CREAM,200],['TO WALK.',112,GOLD,318]],1-ramp(t,2.2,2.4)); }
function then(t){ const u=t-CUT;
  camT(g,K([[0,1.36],[2.2,1.44]],u,x=>x),K([[0,600],[2.2,620]],u),1250); room(0,t); armchair(170,1,{col:'#9a5a3c'}); blocks();
  // toddler wobbles forward holding two of dad's fingers, sits down hard at 0.85, dad lifts him at 1.25-1.75
  const walk=clamp(u/0.85), fall=ramp(u,0.85,1.05,out3), lift=ramp(u,1.3,1.85);
  const kx=lerp(620,690,walk)+lerp(0,20,fall)*(1-lift);
  const ph=u*9.5, st=Math.sin(ph)*18*(1-fall*(1-lift));
  const kHipY=FL-126+Math.abs(Math.sin(ph))*-4 + fall*(1-lift)*58;
  const kLegs=fall*(1-lift)>0.3?{near:[kx+58,FL-12],far:[kx+44,FL-12]}:{near:[kx+st+6,FL-12-Math.max(0,Math.sin(ph))*10],far:[kx-st-6,FL-12-Math.max(0,-Math.sin(ph))*10]};
  const hands=[kx-26,1194+fall*(1-lift)*44];
  const dx=lerp(400,470,walk)+fall*(1-lift)*6;
  const D=figure({x:dx,y:FL-336,f:1,lean:0.58+fall*(1-lift)*0.1,nod:0.3,body:'adult',fit:FIT.dad,legs:{near:[dx+42,FL-22],far:[dx-38,FL-22]},arms:{near:[hands[0]+4,hands[1]-4],far:[hands[0]-12,hands[1]]},
    face:{eye:1,brow:0.4,mouth:0.9}});
  figure({x:kx,y:kHipY,f:1,lean:0.1-fall*(1-lift)*0.15,nod:-0.12,body:'kid',fit:FIT.kid,legs:kLegs,arms:{near:hands,far:[hands[0]-8,hands[1]+4]},elbow:-1,
    face:{eye:fall*(1-lift)>0.5&&u<1.3?0:1,brow:0.3,mouth:fall*(1-lift)>0.5?-0.2:0.9}});
  lines([['HE NEVER SIGHED.',80,CREAM,230]],ramp(u,0.9,1.1));
  counter('FALLS:',u<0.95?0:1,ramp(u,0.9,1.0)); }
function grade(t){ g.setTransform(1,0,0,1,0,0);
  const vg=g.createRadialGradient(W/2,H*0.6,W*0.35,W/2,H*0.6,H*0.8); vg.addColorStop(0,'rgba(0,0,0,0)'); vg.addColorStop(1,'rgba(28,16,10,0.38)'); g.fillStyle=vg; g.fillRect(0,0,W,H);
  const R=rng(Math.floor(t*30)+7), im=g.getImageData(0,0,W,H), d=im.data; for(let i=0;i<d.length;i+=4){ const n=(R()-0.5)*6; d[i]+=n; d[i+1]+=n; d[i+2]+=n; } g.putImageData(im,0,0); }
window.renderAt=t=>{ g.setTransform(S,0,0,S,0,0); g.fillStyle='#48342a'; g.fillRect(0,0,1080,1920);
  if(t<CUT) now(t); else then(t); grade(t); return cv.toDataURL('image/jpeg',0.93); };
window.DUR=DUR;
Promise.all([document.fonts.load('800 40px "Inter"')]).finally(()=>{ window.ready=true; });
