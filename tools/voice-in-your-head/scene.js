// The Voice in Your Head (20 s): chalk stickman on a navy board. Canvas 2D, every frame a pure function of t.
// World units: floor at y=0, man A sits at x=0, man B at x=900. Gold = the inner voice, teal = thinking without words, red = markers only.
const W=1080,H=1920,DUR=20;
const cv=document.getElementById('c');cv.width=W;cv.height=H;const out=cv.getContext('2d');
const buf=document.createElement('canvas');buf.width=W;buf.height=H;const g=buf.getContext('2d');
const CHALK='#efe9d8',GOLD='#f2b84b',TEAL='#5cc8bf',RED='#d63e30',INK='#0a1222';
const MARK='"Marker", "Permanent Marker", sans-serif',MONO='"Liberation Mono", monospace';

// ---------- maths ----------
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),lerp=(a,b,t)=>a+(b-a)*t;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,ss=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};
const back=t=>{const c=1.9;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2);}; // overshoot pop
function mul(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
let rnd=Math.random,BOIL=0;const seed=s=>{rnd=mul(s*7919+BOIL*104729);};const J=a=>(rnd()-.5)*2*a;

// ---------- chalk primitives (world space; Z = current camera zoom) ----------
let Z=1;
function wob(pts,amp){const o=[];for(let i=0;i<pts.length-1;i++){const [x0,y0]=pts[i],[x1,y1]=pts[i+1];const n=Math.max(1,Math.round(Math.hypot(x1-x0,y1-y0)/26));
  for(let k=0;k<n;k++){const u=k/n;o.push([lerp(x0,x1,u)+J(amp),lerp(y0,y1,u)+J(amp)]);}}const l=pts[pts.length-1];o.push([l[0]+J(amp),l[1]+J(amp)]);return o;}
function trace(p,closed){g.beginPath();g.moveTo(p[0][0],p[0][1]);for(let i=1;i<p.length-1;i++){g.quadraticCurveTo(p[i][0],p[i][1],(p[i][0]+p[i+1][0])/2,(p[i][1]+p[i+1][1])/2);}const l=p[p.length-1];g.lineTo(l[0],l[1]);if(closed)g.closePath();}
function partial(pts,f){let L=0;const d=[0];for(let i=1;i<pts.length;i++){L+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);d.push(L);}const T=L*f,o=[pts[0]];
 for(let i=1;i<pts.length;i++){if(d[i]<=T)o.push(pts[i]);else{const u=(T-d[i-1])/(d[i]-d[i-1]);o.push([lerp(pts[i-1][0],pts[i][0],u),lerp(pts[i-1][1],pts[i][1],u)]);break;}}return o.length<2?[pts[0],pts[0]]:o;}
function chalk(pts,o={}){let P=pts;if(o.reveal!==undefined){if(o.reveal<=0)return;if(o.reveal<1)P=partial(pts,o.reveal);}
 const w=(o.w||4)/Math.sqrt(Z),col=o.col||CHALK,amp=o.amp??2,passes=o.passes||2;
 g.save();g.lineCap='round';g.lineJoin='round';g.strokeStyle=col;g.shadowColor=o.glowCol||col;g.shadowBlur=(o.glow??8)*Z;
 for(let k=0;k<passes;k++){g.globalAlpha=(o.alpha??1)*(k?.5:1);g.lineWidth=w*(k?.55:1);trace(wob(P,amp*(k?1.5:1)),o.closed);g.stroke();}g.restore();}
function circ(cx,cy,rx,ry,n=28,rot=0){const p=[];for(let i=0;i<=n;i++){const a=rot+i/n*Math.PI*2;p.push([cx+Math.cos(a)*rx,cy+Math.sin(a)*ry]);}return p;}
function fill(p,col,a=1){g.save();g.globalAlpha=a;g.fillStyle=col;g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p)g.lineTo(q[0],q[1]);g.closePath();g.fill();g.restore();}
function hatch(p,o={}){const xs=p.map(q=>q[0]),ys=p.map(q=>q[1]);const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 g.save();g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p)g.lineTo(q[0],q[1]);g.closePath();g.clip();g.strokeStyle=o.col||CHALK;g.lineCap='round';
 const n=Math.ceil((x1-x0)*(y1-y0)/(o.area||2600)),ang=o.ang??-1.1,dx=Math.cos(ang),dy=Math.sin(ang);
 for(let i=0;i<n;i++){const x=x0+rnd()*(x1-x0),y=y0+rnd()*(y1-y0),l=(o.len||40)*(.4+rnd());g.globalAlpha=(o.alpha||.2)*(.3+rnd()*.7);g.lineWidth=(o.lw||1.6)*(.6+rnd()*.8);
  g.beginPath();g.moveTo(x,y);g.lineTo(x+dx*l,y+dy*l);g.stroke();}g.restore();}

// ---------- the board: navy gradient, eraser smudges and dust with parallax ----------
const SMUDGE=(()=>{const r=mul(11),a=[];for(let i=0;i<26;i++)a.push([r()*3200-1100,r()*2600-2000,180+r()*420,.03+r()*.05,r()*3]);return a;})();
const DUST=(()=>{const r=mul(23),a=[];for(let i=0;i<260;i++)a.push([r()*4000-1500,r()*3200-2400,.25+r()*1.1,r(),r()*6.28]);return a;})();
function board(cam,t){const [cx,cy,z]=cam;g.setTransform(1,0,0,1,0,0);
 const gr=g.createRadialGradient(W*.5,H*.42,80,W*.5,H*.5,H*.85);gr.addColorStop(0,'#16274a');gr.addColorStop(.55,'#0c1730');gr.addColorStop(1,'#050913');g.fillStyle=gr;g.fillRect(0,0,W,H);
 // eraser smudges (far layer, parallax .35)
 const pz=.35+.65*z*.35;for(const [x,y,r,a,rot] of SMUDGE){const sx=(x-cx*.35)*pz+W/2,sy=(y-cy*.35)*pz+H/2;if(sx<-r||sx>W+r||sy<-r||sy>H+r)continue;
  const gg=g.createRadialGradient(sx,sy,0,sx,sy,r*pz);gg.addColorStop(0,`rgba(200,214,235,${a})`);gg.addColorStop(1,'rgba(200,214,235,0)');g.fillStyle=gg;g.save();g.translate(sx,sy);g.rotate(rot);g.scale(1.6,.7);g.translate(-sx,-sy);g.beginPath();g.arc(sx,sy,r*pz,0,7);g.fill();g.restore();}
}
function dust(cam,t){const [cx,cy,z]=cam;g.setTransform(1,0,0,1,0,0);
 for(const [x,y,d,ph,a] of DUST){const pz=z*(.5+d*.6),dx=Math.sin(t*.3+a)*30,dy=-t*12*d+Math.cos(t*.4+a)*20;
  const sx=(x+dx-cx*d)*pz+W/2,sy=(((y+dy-cy*d)%3200+3200)%3200-1600)*pz+H/2;if(sx<0||sx>W||sy<0||sy>H)continue;
  const tw=.25+.35*Math.sin(t*1.7+ph*20);g.fillStyle=`rgba(239,233,216,${tw*.5})`;g.beginPath();g.arc(sx,sy,(1+d*2.2)*Math.min(z,1.4),0,7);g.fill();}}

// ---------- the stickman ----------
const HEAD_Y=-560,HR=170;
// pose: eyes 'open'|'closed'|'squeeze'; peek: one eye open (0..1); ears: hands over ears (0..1); swat: right arm swipe (0..1); look:[dx,dy]
function man(id,x,st,t){seed(id*31+1);
 const tr=st.tremble||0,jx=Math.sin(t*41)*tr*5,jy=Math.cos(t*37)*tr*3;
 const hx=x+jx+(st.lean||0)*20,hy=HEAD_Y+jy+(st.bob||0);
 // floor shadow + cushion
 g.save();const sg=g.createRadialGradient(x,4,10,x,4,330);sg.addColorStop(0,'rgba(0,0,0,.45)');sg.addColorStop(1,'rgba(0,0,0,0)');g.fillStyle=sg;g.scale(1,.18);g.beginPath();g.arc(x,4/.18,330,0,7);g.fill();g.restore();
 const cush=circ(x,-28,250,40,30);fill(cush,INK);hatch(cush,{area:900,len:30,alpha:.22,ang:-.5});chalk(cush,{w:3.4,closed:true});
 // body
 const neck=[hx,hy+HR-4],hip=[x,-120];chalk([neck,[lerp(neck[0],hip[0],.5)+J(2),-260],hip],{w:5.5});
 // crossed legs
 chalk([[x-6,-118],[x-190,-62],[x+70,-34],[x+150,-40]],{w:5.5});chalk([[x+6,-118],[x+190,-62],[x-70,-34],[x-150,-40]],{w:5.5});
 // arms: blend rest (hands on knees) -> ears; right arm can also swat
 const sh=[hx,hy+HR+46];
 for(const sd of [-1,1]){const rest=[[x+sd*120,-250],[x+sd*175,-92]];const ear=[[hx+sd*235,hy+HR*.55],[hx+sd*(HR+18),hy-6]];
  let e=st.ears||0,el=[lerp(rest[0][0],ear[0][0],e),lerp(rest[0][1],ear[0][1],e)],ha=[lerp(rest[1][0],ear[1][0],e),lerp(rest[1][1],ear[1][1],e)];
  if(sd>0&&st.swat>0){const k=Math.sin(st.swat*Math.PI);el=[lerp(el[0],hx+290,k),lerp(el[1],hy+90,k)];ha=[lerp(ha[0],hx+250+st.swat*60,k),lerp(ha[1],hy-170,k)];}
  chalk([sh,el,ha],{w:5});chalk(circ(ha[0],ha[1],17,15,10),{w:3.2,closed:true});}
 // head: dark glass you can see into
 const hp=circ(hx,hy,HR,HR*1.02,40);fill(hp,'#070d1b',.82);
 if(st.inner)st.inner(hx,hy);
 seed(id*31+2);chalk(circ(hx,hy,HR,HR*1.02,26),{w:5,closed:true,glow:10});
 // face
 const [lx,ly]=st.look||[0,0],ey=hy+18;
 for(const sd of [-1,1]){const ex=hx+sd*58+lx*6,er=30;
  let mode=st.eyes||'open';if(sd<0&&st.peek>.5)mode='open';
  if(mode==='open'){const wide=st.wide||0,r=er*(1+wide*.35);g.save();g.fillStyle=CHALK;g.shadowColor=CHALK;g.shadowBlur=10*Z;g.beginPath();g.ellipse(ex,ey,r,r*(st.blink?Math.max(.08,1-st.blink):1),0,0,7);g.fill();g.restore();
   if(!(st.blink>.7)){g.fillStyle=INK;g.beginPath();g.arc(ex+lx*r*.42,ey+ly*r*.42,r*.46,0,7);g.fill();}}
  else if(mode==='closed')chalk([[ex-er,ey+2],[ex,ey+12],[ex+er,ey+2]],{w:4,amp:.6,passes:1});
  else chalk([[ex-er*sd,ey-14],[ex+er*sd*.9,ey],[ex-er*sd,ey+14]],{w:4.2,amp:.6,passes:1});} // squeeze: > <
 // brows (strain)
 if(st.strain>0)for(const sd of [-1,1])chalk([[hx+sd*96,hy-40+st.strain*6],[hx+sd*28,hy-30-st.strain*16]],{w:4,passes:1,alpha:st.strain});
 // mouth
 const m=st.mouth||'flat';
 if(m==='smile')chalk([[hx-36,hy+92],[hx,hy+108],[hx+36,hy+92]],{w:4,passes:1,amp:.6});
 else if(m==='grit')chalk([[hx-40,hy+100],[hx-20,hy+92],[hx,hy+102],[hx+20,hy+92],[hx+40,hy+100]],{w:4,passes:1,amp:.5});
 else if(m==='o'){g.save();g.strokeStyle=CHALK;g.lineWidth=4;g.beginPath();g.ellipse(hx,hy+100,13,18,0,0,7);g.stroke();g.restore();}
 else chalk([[hx-28,hy+100],[hx+28,hy+98]],{w:4,passes:1,amp:.5});
 // sweat
 if(st.sweat>0){const sy=hy-HR*.55+(st.sweat%1)*HR*.9;chalk(circ(hx+HR+16,sy,8,12,10),{w:3,closed:true,alpha:1-(st.sweat%1)*.7});}
 return {hx,hy};
}

// ---------- the inner voice: gold thought bubbles ----------
// [spawn time, text, x, y (world, relative to A's head), size]
const BUB=[
 [3.40,'...',                0,-300, 46],
 [3.95,'OK. SILENCE.',     300,-430, 40],
 [4.50,'AM I DOING IT?',  -290,-320, 40],
 [5.05,"DON'T THINK",      300,-190, 42],
 [5.55,'STOP THINKING',   -290,-520, 40],
 [5.72,'...ABOUT THINKING',250,-610, 36],
 [6.15,'HELLO',              0,-450, 62],
 [6.60,"THAT WON'T WORK", -330,-110, 36],
 [6.92,"IT'S INSIDE",      340,  30, 38],
 [7.18,'DID I LOCK THE DOOR?',-60,-660,36],
 [7.38,'HUNGRY',          -380, 130, 36],
 [7.52,'SHHH',             390,-300, 40],
 [7.66,'HOW LONG LEFT?',  -330, 260, 34],
 [7.80,'WORDS',            370, 220, 36],
 [7.90,'WORDS',           -400,-420, 32],
 [7.97,'WORDS',            400,-520, 30],
];
const SWATTED=3,SWAT_T=5.36,POP_ALL=9.4;
function bubble(i,b,hx,hy,t){const [t0,txt,bx,by,fs]=b;if(t<t0)return;
 let popT=i===SWATTED?SWAT_T:POP_ALL;const pp=clamp((t-popT)/.35);if(pp>=1)return;
 const k=clamp((t-t0)/.32),s=back(k)*(1+pp*.25);
 const tx=hx+bx+Math.sin(t*1.3+i)*10,ty=hy+by+Math.cos(t*1.1+i*2)*8;const px=lerp(hx,tx,ease(k)),py=lerp(hy-40,ty,ease(k));
 g.save();g.globalAlpha=1-pp;g.translate(px,py);g.scale(s,s);
 g.font=`${fs}px ${MARK}`;const tw=g.measureText(txt).width;const rw=tw/2+34,rh=fs*.85+12;
 seed(500+i);const shape=[];for(let a=0;a<=36;a++){const an=a/36*Math.PI*2,r=1+.07*Math.sin(an*9+i);shape.push([Math.cos(an)*rw*r,Math.sin(an)*rh*r]);}
 fill(shape,'#120f08',.85);chalk(shape,{w:3.6,col:GOLD,closed:true,glow:16,amp:1.5});
 g.fillStyle=GOLD;g.shadowColor=GOLD;g.shadowBlur=12*Z;g.textAlign='center';g.textBaseline='middle';g.fillText(txt,0,4);
 g.restore();
 // little trail circles from the head toward the bubble
 if(k>.3&&pp===0){const a=clamp((k-.3)/.4);for(let j=1;j<=2;j++){const u=.25+j*.2;chalk(circ(lerp(hx,px,u),lerp(hy-HR*.6,py+rh*.7,u),7+j*5,7+j*5,10),{w:2.6,col:GOLD,closed:true,glow:10,alpha:a*.8,passes:1});}}
}
function popBurst(hx,hy,t){if(t<POP_ALL||t>POP_ALL+.9)return;const u=(t-POP_ALL)/.9;const r=mul(77);
 for(let i=0;i<BUB.length;i++){if(i===SWATTED)continue;const [,,bx,by]=BUB[i];for(let k=0;k<12;k++){const a=r()*6.28,v=120+r()*260;
  const x=hx+bx+Math.cos(a)*v*u,y=hy+by+Math.sin(a)*v*u+u*u*120;g.fillStyle=`rgba(242,184,75,${(1-u)*.9})`;g.beginPath();g.arc(x,y,(3+r()*5)*(1-u*.5),0,7);g.fill();}}}
function swatBurst(hx,hy,t){const u=(t-SWAT_T)/.6;if(u<0||u>1)return;const r=mul(91),[,,bx,by]=BUB[SWATTED];
 for(let k=0;k<16;k++){const a=r()*6.28,v=80+r()*200;g.fillStyle=`rgba(242,184,75,${(1-u)})`;g.beginPath();g.arc(hx+bx+Math.cos(a)*v*u,hy+by+Math.sin(a)*v*u,3+r()*4,0,7);g.fill();}}
// the HELLO inside the head (frame 0 hook + loop)
function hello(hx,hy,t,a){if(a<=0)return;const k=clamp(t/.28);const s=back(k);
 g.save();g.globalAlpha=a;g.translate(hx,hy-78);g.scale(s*.82,s*.82);
 for(let j=0;j<3;j++){const u=((t*.9+j/3)%1);seed(900+j);chalk(circ(0,0,70+u*120,40+u*70,30),{w:3,col:GOLD,closed:true,glow:14,alpha:(1-u)*.55*a,passes:1});}
 g.font=`64px ${MARK}`;g.textAlign='center';g.textBaseline='middle';g.fillStyle=GOLD;g.shadowColor=GOLD;g.shadowBlur=22*Z;g.fillText('HELLO',0,0);g.restore();}

// ---------- the quiet head: teal pictures, no words ----------
const ICONS={
 sun:(x,y,s)=>{const p=[circ(x,y,22*s,22*s,18)];for(let i=0;i<8;i++){const a=i/8*6.28;p.push([[x+Math.cos(a)*32*s,y+Math.sin(a)*32*s],[x+Math.cos(a)*46*s,y+Math.sin(a)*46*s]]);}return p;},
 wave:(x,y,s)=>{const a=[],b=[];for(let i=0;i<=16;i++){const u=i/16;a.push([x-60*s+u*120*s,y+Math.sin(u*12.5)*12*s]);b.push([x-60*s+u*120*s,y+22*s+Math.sin(u*12.5+1)*10*s]);}return [a,b];},
 tree:(x,y,s)=>[[[x,y+50*s],[x,y]],circ(x,y-26*s,36*s,32*s,18),[[x,y+16*s],[x-18*s,y-4*s]]],
 house:(x,y,s)=>[[[x-40*s,y+40*s],[x-40*s,y],[x,y-34*s],[x+40*s,y],[x+40*s,y+40*s],[x-40*s,y+40*s]],[[x-10*s,y+40*s],[x-10*s,y+14*s],[x+10*s,y+14*s],[x+10*s,y+40*s]]],
 heart:(x,y,s)=>{const p=[];for(let i=0;i<=30;i++){const a=i/30*6.28;p.push([x+16*Math.pow(Math.sin(a),3)*2.4*s,y-(13*Math.cos(a)-5*Math.cos(2*a)-2*Math.cos(3*a)-Math.cos(4*a))*2.4*s]);}return [p];},
 star:(x,y,s)=>{const p=[];for(let i=0;i<=10;i++){const a=-Math.PI/2+i/10*6.28,r=i%2?16:40;p.push([x+Math.cos(a)*r*s,y+Math.sin(a)*r*s]);}return [p];},
};
// picture bubbles: round, teal, no words; each one keeps redrawing a new picture
const PB=[[10.25,-230,-320,['sun','house','wave']],[10.7,230,-350,['tree','heart','star']],[11.2,-110,-560,['wave','star','sun']],[11.75,150,-590,['heart','tree','house']]];
function quietHead(hx,hy,t,a){if(a<=0)return;
 g.save();const gg=g.createRadialGradient(hx,hy-30,10,hx,hy,HR);gg.addColorStop(0,`rgba(92,200,191,${.22*a})`);gg.addColorStop(1,'rgba(92,200,191,0)');g.fillStyle=gg;g.beginPath();g.arc(hx,hy,HR-6,0,7);g.fill();g.restore();}
function pictureBubbles(hx,hy,t){PB.forEach(([t0,bx,by,icons],i)=>{if(t<t0)return;const k=clamp((t-t0)/.5),s=back(k)*.95;
  const px=lerp(hx,hx+bx+Math.sin(t*.8+i)*10,ease(k)),py=lerp(hy-60,hy+by+Math.cos(t*.7+i)*8,ease(k));const R=92;
  if(k>.35)for(let j=1;j<=2;j++){const u=.25+j*.2;seed(800+i*3+j);chalk(circ(lerp(hx,px,u),lerp(hy-HR*.6,py+R*.8,u),6+j*5,6+j*5,10),{w:2.4,col:TEAL,closed:true,glow:10,passes:1,alpha:.8});}
  g.save();g.translate(px,py);g.scale(s,s);seed(820+i);const sh=[];for(let q=0;q<=36;q++){const an=q/36*Math.PI*2,r=1+.06*Math.sin(an*8+i);sh.push([Math.cos(an)*R*r,Math.sin(an)*R*.9*r]);}
  fill(sh,'#061615',.85);chalk(sh,{w:3.4,col:TEAL,closed:true,glow:16,amp:1.4});
  const ph=(t-t0)/1.7,n=Math.floor(ph)%icons.length,f=ph%1,rev=Math.min(1,f*2.2)*(1-ss(.86,1,f));seed(840+i*7+n);
  for(const p of ICONS[icons[n]](0,0,1.05))chalk(p,{w:3.4,col:TEAL,glow:14,reveal:rev,passes:1,amp:.8});g.restore();});}

// ---------- camera: [t, cx, cy, zoom] ----------
const CLOSE=[0,-578,2.2],MED=[0,-686,.95],TWO=[450,-871,.62],BHEAD=[900,-700,1.35];
const CAM=[[0,...CLOSE],[1.85,0,-575,2.32],[2.15,...MED],[3,0,-680,.96],[8,0,-675,.99],[9.4,30,-680,.97],[9.75,110,-690,.93],[10.08,...TWO],[11.4,450,-860,.64],
 [12.6,...BHEAD],[14.3,900,-690,1.4],[15.3,...TWO],[17.6,440,-860,.66],[19.2,...CLOSE],[20,...CLOSE]];
function camAt(t){let i=0;while(i<CAM.length-2&&t>CAM[i+1][0])i++;const [t0,x0,y0,z0]=CAM[i],[t1,x1,y1,z1]=CAM[i+1];const u=ease(clamp((t-t0)/(t1-t0)));
 let cx=lerp(x0,x1,u),cy=lerp(y0,y1,u),z=Math.exp(lerp(Math.log(z0),Math.log(z1),u));
 // a hand-held breath, and a kick on the two hits
 cx+=Math.sin(t*.7)*4/z;cy+=Math.cos(t*.53)*4/z;const kick=(a)=>{const d=t-a;return d>=0&&d<.4?Math.exp(-d*12)*Math.sin(d*70):0;};z*=1+.025*kick(0)+.03*kick(10.08);
 return [cx,cy,z];}

// ---------- overlay text (screen space) ----------
function txt(s,x,y,o={}){g.save();g.font=`${o.bold?'bold ':''}${o.size||64}px ${o.font||MARK}`;g.textAlign=o.align||'center';g.textBaseline='middle';g.globalAlpha=o.alpha??1;
 g.lineJoin='round';g.lineWidth=o.stroke??12;g.strokeStyle='rgba(3,6,14,.95)';g.strokeText(s,x,y);g.fillStyle=o.col||CHALK;g.shadowColor=o.glow||'rgba(0,0,0,0)';g.shadowBlur=o.glow?14:0;g.fillText(s,x,y);g.restore();}
function typed(s,t0,t,cps){const n=Math.floor((t-t0)*cps)+1;return n<1?'':s.slice(0,Math.min(s.length,n));}
function tag(t){txt('SLOW LIGHT',W/2,96,{size:28,font:MONO,col:'rgba(239,233,216,.55)',stroke:6});}
function overlay(t){g.setTransform(1,0,0,1,0,0);
 // hook (typed on frame 0, done by 1.2 s)
 {const a=1-ss(1.9,2.1,t);if(a>0){const s1=typed('SAY "HELLO"',0,t,14),s2=typed('IN YOUR HEAD.',.78,t,16);txt(s1,W/2,250,{size:92,alpha:a});txt(s2,W/2,360,{size:92,alpha:a});}}
 // instruction
 {const a=ss(2.08,2.2,t)*(1-ss(2.95,3.15,t));if(a>0){txt(typed('NOW STAY SILENT.',2.1,t,26),W/2,250,{size:84,alpha:a});txt(typed('5 SECONDS. NO WORDS.',2.4,t,30),W/2,350,{size:58,alpha:a,col:GOLD});}}
 // timer (only goes up)
 {const a=ss(3.0,3.15,t)*(1-ss(POP_ALL,POP_ALL+.3,t));if(a>0){const v=clamp(t-3.0,0,5);const done=t>=8;
  txt('SILENCE',W/2,170,{size:30,font:MONO,col:'rgba(239,233,216,.8)',alpha:a,stroke:7});
  const pulse=done?1+.08*Math.exp(-(t-8)*6):1;g.save();g.translate(W/2,262);g.scale(pulse,pulse);txt(v.toFixed(1)+' s',0,0,{size:104,font:MONO,bold:1,alpha:a,col:done?GOLD:CHALK});g.restore();
  const bx=W/2-300,by=340;g.save();g.globalAlpha=a;g.strokeStyle='rgba(239,233,216,.35)';g.lineWidth=6;g.lineCap='round';g.beginPath();g.moveTo(bx,by);g.lineTo(bx+600,by);g.stroke();
  g.strokeStyle=CHALK;g.beginPath();g.moveTo(bx,by);g.lineTo(bx+600*v/5,by);g.stroke();for(let s=0;s<=5;s++){g.fillStyle='rgba(239,233,216,.6)';g.fillRect(bx+s*120-1.5,by+10,3,12);}
  g.fillStyle=RED;g.shadowColor=RED;g.shadowBlur=12;g.beginPath();g.arc(bx+600*v/5,by,13,0,7);g.fill();g.restore();}}
 // participation question
 {const a=ss(8.05,8.2,t)*(1-ss(9.3,9.5,t));if(a>0)txt(typed('HOW FAR DID YOU GET?',8.05,t,34),W/2,1480,{size:70,alpha:a});}
 // the twist
 {const a=ss(10.15,10.3,t)*(1-ss(12.1,12.4,t));if(a>0){txt(typed('SOME PEOPLE',10.15,t,26),W/2,250,{size:88,alpha:a});txt(typed("DON'T HAVE ONE.",10.6,t,26),W/2,355,{size:88,alpha:a,col:TEAL,glow:'rgba(92,200,191,.6)'});}}
 {const a=ss(12.5,12.7,t)*(1-ss(14.9,15.2,t));if(a>0){g.save();g.globalAlpha=a;g.font=`46px bold ${MONO}`;g.font=`bold 46px ${MONO}`;const s='ANENDOPHASIA',w=g.measureText(s).width+48;g.fillStyle=`rgb(214,62,48)`;
  const y=1380;g.beginPath();g.roundRect(W/2-w/2,y-34,w,68,10);g.fill();g.fillStyle=CHALK;g.textAlign='center';g.textBaseline='middle';g.fillText(s,W/2,y+2);g.restore();
  txt(typed('LITTLE OR NO INNER VOICE.',12.8,t,40),W/2,1462,{size:44,alpha:a});txt(typed('MANY THINK IN PICTURES.',13.3,t,40),W/2,1516,{size:44,alpha:a,col:TEAL});}}
 // the question back to the viewer
 {const a=ss(15.3,15.45,t)*(1-ss(18.4,18.8,t));if(a>0){txt(typed('WHICH ONE',15.3,t,22),W/2,250,{size:96,alpha:a});txt(typed('ARE YOU?',15.75,t,22),W/2,360,{size:96,alpha:a,col:GOLD,glow:'rgba(242,184,75,.5)'});}}
 {const a=ss(15.6,15.9,t)*(1-ss(17.4,17.8,t));if(a>0){const [cx,cy,z]=camAt(t);const sx=wx=>(wx-cx)*z+W/2;txt('A VOICE',sx(0),1572,{size:44,alpha:a,col:GOLD});txt('NO VOICE',sx(900),1572,{size:44,alpha:a,col:TEAL});}}
 tag(t);
}

// ---------- the shot ----------
function scene(t){BOIL=Math.floor(t*10);const cam=camAt(t);const [cx,cy,z]=cam;Z=z;
 board(cam,t);
 g.setTransform(z,0,0,z,W/2-cx*z,H/2-cy*z);
 // floor: one long chalk line and hatched ground
 seed(3);chalk([[-1600,0],[-400,4],[600,-2],[2400,3]],{w:4,alpha:.85});const gp=[[-1600,0],[2400,0],[2400,900],[-1600,900]];fill(gp,'#060b17',.6);hatch(gp,{area:5200,len:70,alpha:.16,ang:-.35});
 // A: the one with the voice
 const swat=clamp((t-5.12)/.42),ears=ss(6.35,6.6,t)*(1-ss(8.3,8.9,t));
 let eyes='open',mouth='flat',look=[.7,-.8],peek=0,strain=0,tremble=0,wide=0,blink=0;
 if(t<2.0){mouth=t>.6?'smile':'flat';}
 else if(t<3.0){eyes=t>2.45?'closed':'open';look=[0,0];}
 else if(t<8.0){eyes='closed';if(t>4.45&&t<4.95)peek=1,look=[-.5,-.6];if(t>5.5){eyes='squeeze';mouth='grit';}strain=ss(5.4,6,t);tremble=ss(6.3,8,t)*1.2;}
 else if(t<10.05){eyes='open';wide=ss(8,8.15,t)*(1-ss(8.6,9.4,t));mouth=t<8.6?'o':'flat';look=[0,0];blink=t>POP_ALL&&t<POP_ALL+.15?1:0;}
 else if(t<17.6){look=[1,-.1];mouth=t>15.3?'smile':'flat';}
 else {look=[lerp(1,.7,ss(17.6,18.6,t)),lerp(-.1,-.8,ss(17.6,18.6,t))];}
 const A={eyes,mouth,look,peek,strain,tremble,wide,blink,ears,swat:t>5.12&&t<5.54?swat:0,sweat:t>5.6&&t<9.4?(t-5.6)*.9:0,bob:Math.sin(t*1.6)*3,
  inner:(hx,hy)=>{hello(hx,hy,t,(t<2.15?1-ss(1.95,2.15,t):0));hello(hx,hy,t-14.6,t>15.3&&t<17.9?ss(15.3,15.6,t)*(1-ss(17.6,17.9,t)):0);}};
 const a=man(1,0,A,t);
 // B: the quiet one, revealed at 10.0 (off-camera before that)
 const B={eyes:'open',mouth:'smile',look:t<15.3?[-.1,-.2]:[-.8,0],blink:(()=>{const p=(t-10.9)%3.4;return p>0&&p<.18?Math.sin(p/.18*Math.PI):0;})(),bob:Math.sin(t*1.1+1)*3,
  inner:(hx,hy)=>quietHead(hx,hy,t,ss(9.9,10.4,t))};
 const bb=man(2,900,B,t);pictureBubbles(bb.hx,bb.hy,t);
 // A's voice, drawn above everything in world space
 for(let i=0;i<BUB.length;i++)bubble(i,BUB[i],a.hx,a.hy,t);
 swatBurst(a.hx,a.hy,t);popBurst(a.hx,a.hy,t);
 dust(cam,t);
 // vignette, grain and the held-breath dim
 g.setTransform(1,0,0,1,0,0);const v=g.createRadialGradient(W/2,H*.48,H*.25,W/2,H*.5,H*.75);v.addColorStop(0,'rgba(0,0,0,0)');v.addColorStop(1,'rgba(0,0,0,.6)');g.fillStyle=v;g.fillRect(0,0,W,H);
 const dim=ss(9.45,9.8,t)*(1-ss(9.98,10.12,t))*.35;if(dim>0){g.fillStyle=`rgba(0,0,0,${dim})`;g.fillRect(0,0,W,H);}
 const flash=t>=10.06&&t<10.26?.12*(1-(t-10.06)/.2):0;if(flash>0){g.fillStyle=`rgba(92,200,191,${flash})`;g.fillRect(0,0,W,H);}
 overlay(t);
}

// grain (fixed noise tile, shifted per frame)
const GR=document.createElement('canvas');GR.width=GR.height=256;{const c=GR.getContext('2d'),d=c.createImageData(256,256),r=mul(5);for(let i=0;i<d.data.length;i+=4){const v=r()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=14;}c.putImageData(d,0,0);}

// motion blur: average sub-frames when the camera moves fast
window.renderAt=function(t){
 const c0=camAt(t),c1=camAt(t+1/60);const sp=Math.hypot((c1[0]-c0[0])*c0[2],(c1[1]-c0[1])*c0[2])+Math.abs(Math.log(c1[2]/c0[2]))*900;
 const S=sp>18?5:sp>7?3:1;out.setTransform(1,0,0,1,0,0);out.clearRect(0,0,W,H);
 for(let k=0;k<S;k++){scene(t+(S>1?(k/(S-1)-.5)/60:0));out.globalAlpha=1/(k+1);out.drawImage(buf,0,0);}
 out.globalAlpha=1;const r=Math.floor(t*30);out.drawImage(GR,-(r*37%256),-(r*91%256),W+512,H+512);
 return cv.toDataURL('image/jpeg',.94);};
document.fonts.load(`64px ${MARK}`).then(()=>document.fonts.load(`bold 40px ${MONO}`)).then(()=>{window.ready=true;});
