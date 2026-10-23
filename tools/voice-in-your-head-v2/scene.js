// The Voice in Your Head V2 (20 s): white scribble-line figures on a blue paper ground. Canvas 2D, every frame a pure function of t.
// World units: floor at y=0. A (the voice) sits at x=0, B (thinks in pictures) at x=760. Gold = words, mint = pictures, red = markers only.
const W=1080,H=1920,DUR=20;
const cv=document.getElementById('c');cv.width=W;cv.height=H;const out=cv.getContext('2d');
const buf=document.createElement('canvas');buf.width=W;buf.height=H;const g=buf.getContext('2d');
const LINE='#f4f1ea',GOLD='#ffd36e',MINT='#9ff0e2',RED='#e0453a',DEEP='#0f2747';
const MARK='"Marker", sans-serif',MONO='"Liberation Mono", monospace';

// ---------- maths ----------
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),lerp=(a,b,t)=>a+(b-a)*t;
const ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,ss=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};
const back=t=>{const c=1.9;return 1+(c+1)*Math.pow(t-1,3)+c*Math.pow(t-1,2);};
function mul(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
let rnd=Math.random,BOIL=0;const seed=s=>{rnd=mul(s*7919+BOIL*104729);};const J=a=>(rnd()-.5)*2*a;

// ---------- scribble-line primitives (world space; Z = camera zoom) ----------
let Z=1;
function smooth(p,closed){g.beginPath();g.moveTo(p[0][0],p[0][1]);for(let i=1;i<p.length-1;i++)g.quadraticCurveTo(p[i][0],p[i][1],(p[i][0]+p[i+1][0])/2,(p[i][1]+p[i+1][1])/2);const l=p[p.length-1];g.lineTo(l[0],l[1]);if(closed)g.closePath();}
function resample(pts,step=24){const o=[];for(let i=0;i<pts.length-1;i++){const [x0,y0]=pts[i],[x1,y1]=pts[i+1];const n=Math.max(1,Math.round(Math.hypot(x1-x0,y1-y0)/step));for(let k=0;k<n;k++){const u=k/n;o.push([lerp(x0,x1,u),lerp(y0,y1,u)]);}}o.push(pts[pts.length-1]);return o;}
function partial(pts,f){let L=0;const d=[0];for(let i=1;i<pts.length;i++){L+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);d.push(L);}const T=L*f,o=[pts[0]];
 for(let i=1;i<pts.length;i++){if(d[i]<=T)o.push(pts[i]);else{const u=(T-d[i-1])/(d[i]-d[i-1]);o.push([lerp(pts[i-1][0],pts[i][0],u),lerp(pts[i-1][1],pts[i][1],u)]);break;}}return o.length<2?[pts[0],pts[0]]:o;}
// several loose passes of one line, like the reference's bundled pen strokes
function pen(pts,o={}){let P=pts;if(o.reveal!==undefined){if(o.reveal<=0)return;if(o.reveal<1)P=partial(pts,o.reveal);}
 const R=resample(P,o.step||24),passes=o.passes??3,amp=o.amp??2.4,w=(o.w||2.6)/Math.pow(Z,.55);
 g.save();g.lineCap='round';g.lineJoin='round';g.strokeStyle=o.col||LINE;g.shadowColor=o.glowCol||o.col||LINE;g.shadowBlur=(o.glow??6)*Z;
 for(let k=0;k<passes;k++){const off=k?J(amp*1.6):0,q=R.map(([x,y])=>[x+J(amp)+off,y+J(amp)+off*.6]);g.globalAlpha=(o.alpha??1)*(k?.55:1);g.lineWidth=w*(k?.7:1);smooth(q,o.closed);g.stroke();}
 g.restore();}
function circ(cx,cy,rx,ry,n=28,rot=0){const p=[];for(let i=0;i<=n;i++){const a=rot+i/n*Math.PI*2;p.push([cx+Math.cos(a)*rx,cy+Math.sin(a)*ry]);}return p;}
function fill(p,col,a=1){g.save();g.globalAlpha=a;g.fillStyle=col;g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p)g.lineTo(q[0],q[1]);g.closePath();g.fill();g.restore();}
// a limb drawn as flowing contour lines: two outline curves plus inner strands
function tube(P,w0,w1,o={}){const R=resample(P,20),n=R.length;const side=(s,k)=>R.map(([x,y],i)=>{const a=R[Math.max(0,i-1)],b=R[Math.min(n-1,i+1)];let nx=-(b[1]-a[1]),ny=b[0]-a[0];const l=Math.hypot(nx,ny)||1;nx/=l;ny/=l;const w=lerp(w0,w1,i/(n-1))*s*k;return [x+nx*w,y+ny*w];});
 const body=[...side(1,1),...side(-1,1).reverse()];fill(body,DEEP,.35);
 for(const k of [1,-1])pen(side(k,1),{...o,passes:3});
 for(const k of [.45,-.2])pen(side(k,1),{...o,passes:1,alpha:.45,w:1.8});
 const e=R[n-1],s=R[0];pen(circ(e[0],e[1],w1,w1,14),{...o,passes:2,alpha:.8,w:2});}

// ---------- the paper: blue ground, fibres, vignette ----------
const FIB=(()=>{const r=mul(11),a=[];for(let i=0;i<340;i++)a.push([r()*1400-160,r()*2300-190,20+r()*90,r()*6.28,.03+r()*.05]);return a;})();
const MOTES=(()=>{const r=mul(23),a=[];for(let i=0;i<160;i++)a.push([r()*3600-1300,r()*3000-2300,.3+r(),r()*6.28]);return a;})();
function paper(cam,t,tint){g.setTransform(1,0,0,1,0,0);
 const gr=g.createRadialGradient(W*.5,H*.45,60,W*.5,H*.5,H*.8);gr.addColorStop(0,tint?'#3b72ad':'#356aa3');gr.addColorStop(.6,'#24507f');gr.addColorStop(1,'#132d4e');g.fillStyle=gr;g.fillRect(0,0,W,H);
 g.strokeStyle='#cfe0f5';g.lineCap='round';for(const [x,y,l,a,al] of FIB){g.globalAlpha=al;g.lineWidth=1;g.beginPath();g.moveTo(x,y);g.lineTo(x+Math.cos(a)*l,y+Math.sin(a)*l);g.stroke();}g.globalAlpha=1;}
function motes(cam,t){const [cx,cy,z]=cam;g.setTransform(1,0,0,1,0,0);
 for(const [x,y,d,ph] of MOTES){const pz=z*(.5+d*.6),sx=(x+Math.sin(t*.3+ph)*30-cx*d)*pz+W/2,sy=(((y-t*14*d-cy*d)%3000+3000)%3000-1500)*pz+H/2;if(sx<0||sx>W||sy<0||sy>H)continue;
  g.fillStyle=`rgba(244,241,234,${(.2+.25*Math.sin(t*1.5+ph*9))*.6})`;g.beginPath();g.arc(sx,sy,(1+d*2)*Math.min(z,1.4),0,7);g.fill();}}

// ---------- the figure (seated, cross-legged, front view) ----------
const HEAD_Y=-560,HR=135;
function figure(id,x,st,t){seed(id*31+1);
 const tr=st.tremble||0,jx=Math.sin(t*43)*tr*4,jy=Math.cos(t*37)*tr*3,hx=x+jx,hy=HEAD_Y+jy+(st.bob||0);
 // floor shadow
 g.save();const sg=g.createRadialGradient(x,0,10,x,0,320);sg.addColorStop(0,'rgba(8,20,40,.5)');sg.addColorStop(1,'rgba(8,20,40,0)');g.fillStyle=sg;g.scale(1,.16);g.beginPath();g.arc(x,0,320,0,7);g.fill();g.restore();
 // legs: two crossed tubes (thigh to knee, shin back under)
 tube([[x-40,-115],[x-150,-80],[x-245,-52],[x-200,-24],[x-40,-26],[x+70,-30]],44,34,{});
 tube([[x+40,-115],[x+150,-80],[x+245,-52],[x+200,-22],[x+40,-20],[x-70,-24]],44,34,{});
 // torso contours
 const sh=hy+HR+40;const L=[[x-58,sh],[x-80,sh+70],[x-72,-260],[x-92,-120]],Rr=L.map(([px,py])=>[2*x-px,py]);
 fill([...L,...Rr.slice().reverse()],DEEP,.35);pen(L,{passes:3});pen(Rr,{passes:3});pen([[x-30,sh+40],[x-38,-200],[x-46,-130]],{passes:1,alpha:.4,w:1.8});pen([[x+24,sh+50],[x+30,-180]],{passes:1,alpha:.4,w:1.8});
 pen([[x-92,-118],[x,-104],[x+92,-118]],{passes:2});
 // neck
 pen([[hx-26,hy+HR-14],[x-30,sh+6]],{passes:2});pen([[hx+26,hy+HR-14],[x+30,sh+6]],{passes:2});
 // arms: rest (hands on knees) -> ears; the right arm can swat
 for(const sd of [-1,1]){const s0=[x+sd*70,sh+18];let el=[x+sd*135,-250],ha=[x+sd*175,-100];
  const e=st.ears||0;el=[lerp(el[0],hx+sd*215,e),lerp(el[1],hy+HR*.7,e)];ha=[lerp(ha[0],hx+sd*(HR+10),e),lerp(ha[1],hy-4,e)];
  if(sd>0&&st.swat>0){const k=Math.sin(st.swat*Math.PI);el=[lerp(el[0],hx+260,k),lerp(el[1],hy+60,k)];ha=[lerp(ha[0],hx+230+st.swat*80,k),lerp(ha[1],hy-190,k)];}
  if(st.wave&&sd<0){const k=st.wave;el=[lerp(el[0],x-190,k),lerp(el[1],sh-40,k)];ha=[lerp(ha[0],x-215+Math.sin(t*9)*25*k,k),lerp(ha[1],sh-200,k)];}
  tube([s0,el,ha],22,16,{});}
 // head: dark glass with the thought storm behind the face
 fill(circ(hx,hy,HR,HR*1.03,40),DEEP,.55);
 if(st.inner)st.inner(hx,hy);
 seed(id*31+5);pen(circ(hx,hy,HR,HR*1.03,30),{passes:4,closed:true,w:2.8,amp:3});
 // face
 const [lx,ly]=st.look||[0,0],ey=hy+10;
 for(const sd of [-1,1]){const ex=hx+sd*48+lx*5,er=27*(1+(st.wide||0)*.3);let mode=st.eyes||'open';if(sd<0&&st.peek)mode='open';
  g.save();g.fillStyle=DEEP;g.globalAlpha=.85;g.beginPath();g.arc(ex,ey,er+8,0,7);g.fill();g.restore();
  if(mode==='open'){const bl=st.blink||0;g.save();g.fillStyle=LINE;g.shadowColor=LINE;g.shadowBlur=8*Z;g.beginPath();g.ellipse(ex,ey,er,er*Math.max(.08,1-bl),0,0,7);g.fill();g.restore();
   if(bl<.7){g.fillStyle='#10233f';g.beginPath();g.arc(ex+lx*er*.45,ey+ly*er*.45,er*.48,0,7);g.fill();}}
  else if(mode==='closed')pen([[ex-er,ey+2],[ex,ey+11],[ex+er,ey+2]],{passes:2,amp:.6,w:3.4});
  else pen([[ex-er*sd,ey-13],[ex+er*sd*.9,ey],[ex-er*sd,ey+13]],{passes:2,amp:.6,w:3.4});}
 if(st.strain>0)for(const sd of [-1,1])pen([[hx+sd*84,hy-34+st.strain*5],[hx+sd*24,hy-26-st.strain*15]],{passes:2,alpha:st.strain,w:3});
 const m=st.mouth||'flat',my=hy+78;
 if(m==='smile')pen([[hx-30,my],[hx,my+14],[hx+30,my]],{passes:2,amp:.6,w:3.2});
 else if(m==='grit')pen([[hx-34,my+4],[hx-17,my-4],[hx,my+5],[hx+17,my-4],[hx+34,my+4]],{passes:2,amp:.5,w:3});
 else if(m==='o'){g.save();g.strokeStyle=LINE;g.lineWidth=3.4;g.beginPath();g.ellipse(hx,my+4,11,15,0,0,7);g.stroke();g.restore();}
 else pen([[hx-24,my+4],[hx+24,my+2]],{passes:2,amp:.5,w:3});
 if(st.sweat>0){const sy=hy-HR*.5+(st.sweat%1)*HR*.9;pen(circ(hx+HR+14,sy,7,11,10),{closed:true,passes:2,alpha:1-(st.sweat%1)*.7});}
 return {hx,hy};}

// ---------- A's thought storm: loops that pile up around the head (the reference's scribbled head) ----------
const STORM=(()=>{const r=mul(41),a=[];for(let i=0;i<70;i++){const ang=r()*6.28,d=Math.sqrt(r());a.push([ang,d,40+r()*80,25+r()*60,r()*3,r()*6.28,r()<.18]);}return a;})();
function storm(hx,hy,t,n,col){const N=Math.floor(n);for(let i=0;i<N;i++){const [ang,d,rx,ry,rot,ph,gold]=STORM[i];const f=Math.min(1,n-i);
  const sp=1+d*.6,cx=hx+Math.cos(ang+t*.25*(i%2?1:-1))*d*HR*1.25,cy=hy-HR*.25+Math.sin(ang+t*.25*(i%2?1:-1))*d*HR*1.05;seed(1000+i);
  pen(circ(cx,cy,rx*sp*.8,ry*sp*.8,22,rot+t*(.6+d)*(i%2?1:-1)),{closed:true,passes:1,w:2,amp:3,alpha:.55*f,col:gold?col:LINE,glow:5});}}

// ---------- A's intrusive thoughts: big gold bubbles ----------
// [spawn, text, x, y (relative to A's head), font size]
const BUB=[
 [3.70,'...',                 0,-250, 70, 7.5],
 [4.30,'IS THIS WORKING?', -200,-410, 56],
 [5.00,"DON'T THINK.",      250,-260, 58],
 [5.70,'STOP THINKING',    -250,-150, 54],
 [5.86,'...ABOUT THINKING', 285,-390, 44],
 [6.50,'DID I LOCK THE DOOR?',60,-545, 52],
 [7.10,"IT'S INSIDE.",      270, 170, 54],
 [7.55,'HELLO',             -10,-275, 92],
 [7.85,'SHHH!',            -290, 160, 60],
];
const SWATTED=2,SWAT_T=5.42,SNAP=9.0;
function bubble(i,b,hx,hy,t){const [t0,txt,bx,by,fs,tEnd]=b;if(t<t0||t>=SNAP||(tEnd&&t>=tEnd))return;
 if(i===SWATTED&&t>SWAT_T+.3)return;const pp=i===SWATTED?clamp((t-SWAT_T)/.3):0;
 const k=clamp((t-t0)/.3),s=back(k)*(1+pp*.3);
 const tx=hx+bx+Math.sin(t*1.4+i)*9,ty=hy+by+Math.cos(t*1.2+i*2)*7,px=lerp(hx,tx,ease(k)),py=lerp(hy-40,ty,ease(k));
 g.save();g.globalAlpha=1-pp;g.translate(px,py);g.scale(s,s);g.font=`${fs}px ${MARK}`;const tw=g.measureText(txt).width,rw=tw/2+40,rh=fs*.8+18;
 seed(500+i);const sh=[];for(let a=0;a<=40;a++){const an=a/40*Math.PI*2,r=1+.06*Math.sin(an*9+i);sh.push([Math.cos(an)*rw*r,Math.sin(an)*rh*r]);}
 fill(sh,'#13233d',.88*(1-pp));pen(sh,{closed:true,col:GOLD,passes:3,glow:14,w:3,amp:1.6,alpha:1-pp});
 g.globalAlpha=1-pp;g.fillStyle=GOLD;g.shadowColor=GOLD;g.shadowBlur=10*Z;g.textAlign='center';g.textBaseline='middle';g.fillText(txt,0,4);g.restore();
 if(k>.3&&!pp){const a=clamp((k-.3)/.4);for(let j=1;j<=2;j++){const u=.22+j*.2;seed(560+i*3+j);pen(circ(lerp(hx,px,u),lerp(hy-HR*.7,py+rh*.8,u),6+j*5,6+j*5,10),{closed:true,col:GOLD,passes:1,alpha:a*.8,w:2.4});}}}
function swatBurst(hx,hy,t){const u=(t-SWAT_T)/.6;if(u<0||u>1)return;const r=mul(91),[,,bx,by]=BUB[SWATTED];
 for(let k=0;k<18;k++){const a=r()*6.28,v=80+r()*220;g.fillStyle=`rgba(255,211,110,${1-u})`;g.beginPath();g.arc(hx+bx+Math.cos(a)*v*u,hy+by+Math.sin(a)*v*u,3+r()*4,0,7);g.fill();}}
// the big HELLO inside the head (frame 0, the return at 7.55 is a bubble, and the loop re-forms it)
function hello(hx,hy,t,a,draw=1){if(a<=0)return;const k=clamp(t/.25);const s=1+.15*(1-ease(k));
 g.save();g.globalAlpha=a;g.translate(hx,hy-62);g.scale(s,s);
 for(let j=0;j<3;j++){const u=((Math.max(0,t)*.8+j/3)%1);seed(900+j);pen(circ(0,0,60+u*130,32+u*70,30),{closed:true,col:GOLD,passes:1,alpha:(1-u)*.6*a*draw,w:2.4,glow:12});}
 g.font=`74px ${MARK}`;g.textAlign='center';g.textBaseline='middle';g.lineWidth=5;g.strokeStyle='#13233d';g.strokeText('HELLO',0,0);g.fillStyle=GOLD;g.shadowColor=GOLD;g.shadowBlur=20*Z;
 if(draw<1){const w=g.measureText('HELLO').width;g.beginPath();g.rect(-w/2-10,-60,(w+20)*draw,120);g.clip();}
 g.fillText('HELLO',0,0);g.restore();}

// ---------- B: thinks in pictures (mint drawings, no words) ----------
const ICONS={
 sun:(x,y,s)=>{const p=[circ(x,y,22*s,22*s,18)];for(let i=0;i<8;i++){const a=i/8*6.28;p.push([[x+Math.cos(a)*32*s,y+Math.sin(a)*32*s],[x+Math.cos(a)*46*s,y+Math.sin(a)*46*s]]);}return p;},
 wave:(x,y,s)=>{const a=[],b=[];for(let i=0;i<=16;i++){const u=i/16;a.push([x-60*s+u*120*s,y+Math.sin(u*12.5)*12*s]);b.push([x-60*s+u*120*s,y+24*s+Math.sin(u*12.5+1)*10*s]);}return [a,b];},
 tree:(x,y,s)=>[[[x,y+50*s],[x,y]],circ(x,y-26*s,36*s,32*s,18),[[x,y+16*s],[x-18*s,y-4*s]]],
 house:(x,y,s)=>[[[x-40*s,y+40*s],[x-40*s,y],[x,y-34*s],[x+40*s,y],[x+40*s,y+40*s],[x-40*s,y+40*s]],[[x-10*s,y+40*s],[x-10*s,y+14*s],[x+10*s,y+14*s],[x+10*s,y+40*s]]],
 heart:(x,y,s)=>{const p=[];for(let i=0;i<=30;i++){const a=i/30*6.28;p.push([x+16*Math.pow(Math.sin(a),3)*2.4*s,y-(13*Math.cos(a)-5*Math.cos(2*a)-2*Math.cos(3*a)-Math.cos(4*a))*2.4*s]);}return [p];},
 star:(x,y,s)=>{const p=[];for(let i=0;i<=10;i++){const a=-Math.PI/2+i/10*6.28,r=i%2?16:40;p.push([x+Math.cos(a)*r*s,y+Math.sin(a)*r*s]);}return [p];},
 cat:(x,y,s)=>[circ(x,y,30*s,26*s,18),[[x-24*s,y-14*s],[x-20*s,y-42*s],[x-6*s,y-24*s]],[[x+24*s,y-14*s],[x+20*s,y-42*s],[x+6*s,y-24*s]],[[x-40*s,y+4*s],[x-14*s,y+6*s]],[[x+40*s,y+4*s],[x+14*s,y+6*s]]],
 moon:(x,y,s)=>{const a=[];for(let i=0;i<=20;i++){const u=-Math.PI/2+i/20*Math.PI;a.push([x+Math.cos(u)*34*s,y+Math.sin(u)*34*s]);}for(let i=20;i>=0;i--){const u=-Math.PI/2+i/20*Math.PI;a.push([x+Math.cos(u)*14*s,y+Math.sin(u)*34*s]);}return [a];},
};
// picture bubbles above B: [spawn, dx, dy, icon cycle]
const PB=[[10.25,-200,-330,['sun','moon','star']],[10.55,190,-350,['house','tree','cat']],[10.9,-10,-560,['heart','wave','sun']]];
function pictureBubbles(hx,hy,t,big){PB.forEach(([t0,bx,by,icons],i)=>{if(t<t0)return;const k=clamp((t-t0)/.45),s=back(k)*(big||1);
  const px=lerp(hx,hx+bx*(big||1)+Math.sin(t*.8+i)*10,ease(k)),py=lerp(hy-60,hy+by*(big||1)+Math.cos(t*.7+i)*8,ease(k)),R=104;
  if(k>.35)for(let j=1;j<=2;j++){const u=.22+j*.2;seed(800+i*3+j);pen(circ(lerp(hx,px,u),lerp(hy-HR*.7,py+R*.8*s,u),6+j*5,6+j*5,10),{closed:true,col:MINT,passes:1,alpha:.85,w:2.4});}
  g.save();g.translate(px,py);g.scale(s,s);seed(820+i);const sh=[];for(let q=0;q<=36;q++){const an=q/36*Math.PI*2,r=1+.06*Math.sin(an*8+i);sh.push([Math.cos(an)*R*r,Math.sin(an)*R*.9*r]);}
  fill(sh,'#0f2c3a',.85);pen(sh,{closed:true,col:MINT,passes:3,glow:14,w:3,amp:1.4});
  const ph=(t-t0)/1.6,n=Math.floor(ph)%icons.length,f=ph%1,rev=Math.min(1,f*2.4)*(1-ss(.88,1,f));seed(840+i*7+n);
  for(const p of ICONS[icons[n]](0,0,1.2))pen(p,{col:MINT,glow:12,reveal:rev,passes:2,amp:.8,w:3});g.restore();});}
// pictures drift inside B's head too
function quietHead(hx,hy,t){g.save();g.beginPath();g.arc(hx,hy,HR-8,0,7);g.clip();const gg=g.createRadialGradient(hx,hy-30,10,hx,hy,HR);gg.addColorStop(0,'rgba(159,240,226,.25)');gg.addColorStop(1,'rgba(159,240,226,0)');g.fillStyle=gg;g.fillRect(hx-HR,hy-HR,HR*2,HR*2);
 [['star',-70,-75],['wave',70,-80]].forEach(([n,dx,dy],i)=>{const f=((t*.4+i*.5)%1),rev=Math.min(1,f*2)*(1-ss(.85,1,f));seed(870+i);for(const p of ICONS[n](hx+dx,hy+dy,.55))pen(p,{col:MINT,glow:10,reveal:rev,passes:1,w:2.4,alpha:.9});});g.restore();}
// A in the two-shot: words keep cycling above the head (animated, not a diagram)
const WORDS=['HELLO?','REPLY LATER.','WHAT TIME?','SAY IT RIGHT.','HELLO','ONE MORE THING'];
function wordStream(hx,hy,t,t0){if(t<t0)return;[[40,-330],[110,-520]].forEach(([bx,by],i)=>{const ph=(t-t0+i*.8)/1.6,n=(Math.floor(ph)*2+i)%WORDS.length,f=ph%1;
  const a=ss(0,.12,f)*(1-ss(.86,1,f)),s=back(clamp(f/.2));if(a<=0)return;const txt=WORDS[n],fs=62;
  g.save();g.translate(hx+bx+Math.sin(t+i)*8,hy+by-f*30);g.scale(s,s);g.font=`${fs}px ${MARK}`;const tw=g.measureText(txt).width,rw=tw/2+34,rh=fs*.8+16;
  seed(600+i);const sh=[];for(let q=0;q<=36;q++){const an=q/36*Math.PI*2,r=1+.06*Math.sin(an*9+i);sh.push([Math.cos(an)*rw*r,Math.sin(an)*rh*r]);}
  fill(sh,'#13233d',.88*a);pen(sh,{closed:true,col:GOLD,passes:3,glow:12,w:3,amp:1.4,alpha:a});g.globalAlpha=a;g.fillStyle=GOLD;g.textAlign='center';g.textBaseline='middle';g.fillText(txt,0,3);g.restore();});}

// ---------- camera: [t, cx, cy, zoom] ----------
const CLOSE=[0,-585,2.3],MED=[0,-600,1.0],SPLIT=[380,-769,.78],SILENT=[0,-620,1.65],BCLOSE=[760,-720,1.25];
const CAM=[[0,...CLOSE],[2.15,0,-582,2.4],[2.75,...MED],[3.4,0,-600,1.0],[8.2,0,-610,1.1],[8.999,0,-610,1.1],[9.0,...SILENT],[9.95,0,-618,1.66],[10.3,...SPLIT],[12.4,380,-760,.8],
 [13.0,...BCLOSE],[14.7,760,-715,1.29],[15.3,...SPLIT],[17.9,380,-760,.8],[19.6,...CLOSE],[20,...CLOSE]];
function camAt(t){let i=0;while(i<CAM.length-2&&t>CAM[i+1][0])i++;const [t0,x0,y0,z0]=CAM[i],[t1,x1,y1,z1]=CAM[i+1];const u=ease(clamp((t-t0)/(t1-t0)));
 let cx=lerp(x0,x1,u),cy=lerp(y0,y1,u),z=Math.exp(lerp(Math.log(z0),Math.log(z1),u));
 const still=t>=9&&t<9.95?0:1;cx+=still*Math.sin(t*.7)*4/z;cy+=still*Math.cos(t*.53)*4/z;
 const shake=ss(7.1,8.2,t)*(1-ss(8.9,9,t));cx+=Math.sin(t*31)*shake*5/z;cy+=Math.cos(t*27)*shake*4/z;
 const kick=a=>{const d=t-a;return d>=0&&d<.4?Math.exp(-d*12)*Math.sin(d*70):0;};z*=1+.025*kick(0)+.035*kick(10);return [cx,cy,z];}

// ---------- screen text ----------
function txt(s,x,y,o={}){if(!s)return;g.save();g.font=`${o.bold?'bold ':''}${o.size||64}px ${o.font||MARK}`;g.textAlign=o.align||'center';g.textBaseline='middle';g.globalAlpha=o.alpha??1;
 g.lineJoin='round';g.lineWidth=o.stroke??13;g.strokeStyle='rgba(9,22,42,.95)';g.strokeText(s,x,y);g.fillStyle=o.col||LINE;g.shadowColor=o.glow||'rgba(0,0,0,0)';g.shadowBlur=o.glow?14:0;g.fillText(s,x,y);g.restore();}
function typed(s,t0,t,cps){const n=Math.floor((t-t0)*cps)+1;return n<1?'':s.slice(0,Math.min(s.length,n));}
function chip(s,y,a,size=46){g.save();g.globalAlpha=a;g.font=`bold ${size}px ${MONO}`;const w=g.measureText(s).width+48;g.fillStyle=RED;g.beginPath();g.roundRect(W/2-w/2,y-size*.75,w,size*1.5,10);g.fill();g.fillStyle=LINE;g.textAlign='center';g.textBaseline='middle';g.fillText(s,W/2,y+2);g.restore();}
function overlay(t){g.setTransform(1,0,0,1,0,0);
 txt('SLOW LIGHT',W/2,96,{size:28,font:MONO,col:'rgba(244,241,234,.6)',stroke:6});
 // 0-2.2 participation hook (typed by 1.1 s)
 {const a=1-ss(2.1,2.3,t);if(a>0){const pk=1+.12*(1-ease(clamp(t/.3)));g.save();g.translate(W/2,295);g.scale(pk,pk);txt('CAN YOU HEAR THIS',0,-50,{size:84,alpha:a});txt('WITHOUT SPEAKING?',0,50,{size:84,alpha:a,col:GOLD,glow:'rgba(255,211,110,.5)'});g.restore();}}
 // 2.3-3.3 the experiment
 {const a=ss(2.25,2.35,t)*(1-ss(3.2,3.4,t));if(a>0){txt(typed('QUICK EXPERIMENT:',2.25,t,40),W/2,230,{size:50,alpha:a,col:GOLD});txt(typed('5 SECONDS. NO WORDS.',2.5,t,40),W/2,325,{size:80,alpha:a});}}
 // 3.2-8.2 the timer (only goes up)
 {const a=ss(3.2,3.35,t)*(1-ss(8.6,8.8,t));if(a>0){const v=clamp(t-3.2,0,5),done=t>=8.2;
  const pulse=done?1+.1*Math.exp(-(t-8.2)*6):1;g.save();g.translate(W/2,230);g.scale(pulse,pulse);txt(v.toFixed(1)+' s',0,0,{size:112,font:MONO,bold:1,alpha:a,col:done?GOLD:LINE});g.restore();
  const bx=W/2-300,by=318;g.save();g.globalAlpha=a;g.lineCap='round';g.strokeStyle='rgba(244,241,234,.35)';g.lineWidth=7;g.beginPath();g.moveTo(bx,by);g.lineTo(bx+600,by);g.stroke();
  g.strokeStyle=LINE;g.beginPath();g.moveTo(bx,by);g.lineTo(bx+600*v/5,by);g.stroke();g.fillStyle=RED;g.shadowColor=RED;g.shadowBlur=12;g.beginPath();g.arc(bx+600*v/5,by,14,0,7);g.fill();g.restore();
  txt('JUST FOR FUN · NOT A TEST',W/2,372,{size:26,font:MONO,alpha:a*(1-ss(6.2,6.4,t)),col:'rgba(244,241,234,.75)',stroke:6});}}
 // 8.2-9.95 the question, held over the silent head
 {const a=ss(8.95,9.0,t)*(1-ss(9.85,9.98,t));if(a>0){const pk=1+.1*(1-ease(clamp((t-9)/.25)));g.save();g.translate(W/2,480);g.scale(pk,pk);txt('HOW LONG',0,-56,{size:100,alpha:a});txt('DID YOU LAST?',0,56,{size:100,alpha:a,col:GOLD,glow:'rgba(255,211,110,.5)'});g.restore();}}
 // 10-12.6 the twist
 {const a=ss(10.1,10.2,t)*(1-ss(12.6,12.85,t));if(a>0){txt(typed('SOME PEOPLE THINK',10.1,t,32),W/2,235,{size:80,alpha:a});txt(typed('WITHOUT WORDS.',10.6,t,30),W/2,335,{size:96,alpha:a,col:MINT,glow:'rgba(159,240,226,.6)'});}}
 {const a=ss(10.7,10.9,t)*(1-ss(12.6,12.85,t));if(a>0){const [cx,cy,z]=camAt(t),sx=wx=>(wx-cx)*z+W/2;txt('WORDS',sx(0),1590,{size:54,alpha:a,col:GOLD});txt('PICTURES',sx(760),1590,{size:54,alpha:a,col:MINT});}}
 // 12.9-15.2 the name
 {const a=ss(12.9,13.05,t)*(1-ss(15.0,15.25,t));if(a>0){txt(typed('MANY THINK IN PICTURES.',12.9,t,36),W/2,250,{size:72,alpha:a,col:MINT,glow:'rgba(159,240,226,.5)'});
  chip('ANENDOPHASIA',1420,a);txt(typed('LITTLE OR NO INNER VOICE',13.3,t,40),W/2,1505,{size:50,alpha:a});txt('Nedergaard & Lupyan, Psychological Science, 2024',W/2,1560,{size:24,font:MONO,alpha:a*.85,stroke:5});}}
 // 15.3-18.6 the comment question
 {const a=ss(15.3,15.45,t)*(1-ss(18.5,18.8,t));if(a>0){txt(typed('DO YOU HEAR A VOICE',15.3,t,34),W/2,240,{size:78,alpha:a});txt(typed('WHEN YOU THINK?',15.85,t,30),W/2,340,{size:92,alpha:a,col:GOLD,glow:'rgba(255,211,110,.5)'});
  const b=ss(16.5,16.7,t)*a;txt('COMMENT:',W/2,1540,{size:40,font:MONO,bold:1,alpha:b,stroke:7});
  if(b>0){g.save();g.globalAlpha=b;g.font=`62px ${MARK}`;const w1=g.measureText('WORDS ').width,w2=g.measureText('OR ').width,w3=g.measureText('PICTURES').width,x0=W/2-(w1+w2+w3)/2;g.restore();
   txt('WORDS',x0,1618,{size:62,alpha:b,col:GOLD,align:'left'});txt('OR',x0+w1,1618,{size:62,alpha:b,align:'left'});txt('PICTURES',x0+w1+w2,1618,{size:62,alpha:b,col:MINT,align:'left'});}}}
}

// ---------- the shot ----------
function scene(t){BOIL=Math.floor(t*10);const cam=camAt(t),[cx,cy,z]=cam;Z=z;
 paper(cam,t,t>=10);
 g.setTransform(z,0,0,z,W/2-cx*z,H/2-cy*z);
 seed(3);pen([[-1700,0],[-400,3],[700,-2],[2400,2]],{passes:3,alpha:.85});
 // A: the voice
 const silent=t>=SNAP&&t<9.95;
 let eyes='open',mouth='flat',look=[.6,-.8],peek=0,strain=0,tremble=0,wide=0,blink=0,ears=0,swat=0,wave=0;
 if(t<2.3){mouth=t>.5?'smile':'flat';}
 else if(t<3.2){eyes=t>2.85?'closed':'open';look=[0,0];}
 else if(t<SNAP){eyes='closed';if(t>4.3&&t<4.9){peek=1;look=[-.5,-.7];}if(t>5.65){eyes='squeeze';mouth='grit';}strain=ss(5.5,6.2,t);tremble=ss(6.4,8.6,t)*1.3;ears=ss(6.9,7.15,t);
  if(t>5.0&&t<5.5)swat=clamp((t-5.0)/.5);if(t>8.2){eyes='open';wide=1;mouth='o';}}
 else if(t<9.95){eyes='open';look=[0,0];mouth='flat';blink=t>9.35&&t<9.5?Math.sin((t-9.35)/.15*Math.PI):0;}
 else if(t<17.9){look=[.9,-.1];mouth=t>15.3?'smile':'flat';if(t>15.6&&t<17.4)wave=ss(15.6,15.9,t)*(1-ss(17.1,17.4,t));}
 else {look=[lerp(.9,.6,ss(17.9,19,t)),lerp(-.1,-.8,ss(17.9,19,t))];mouth=t>19.4?'smile':'flat';}
 const noise=t<3.2?0:t<SNAP?Math.pow(clamp((t-3.4)/4.8),1.6)*70:0;
 const A={eyes,mouth,look,peek,strain,tremble,wide,blink,ears,swat,wave,sweat:t>5.8&&t<SNAP?(t-5.8)*.9:0,bob:Math.sin(t*1.6)*3,
  inner:(hx,hy)=>{if(!silent){storm(hx,hy,t,noise,GOLD);if(t>=10&&t<17.9)storm(hx,hy,t,18,GOLD);}
   hello(hx,hy,t,t<2.3?1-ss(2.1,2.3,t):0);hello(hx,hy,t,t>19.3?1:0,clamp((t-19.3)/.6));}};
 const a=figure(1,0,A,t);
 // B: pictures
 const B={eyes:'open',mouth:'smile',look:t<15.3?[-.1,-.3]:[-.8,0],blink:(()=>{const p=(t-11.3)%3.1;return p>0&&p<.18?Math.sin(p/.18*Math.PI):0;})(),bob:Math.sin(t*1.1+1)*3,
  wave:t>15.9&&t<17.6?ss(15.9,16.2,t)*(1-ss(17.3,17.6,t)):0,inner:(hx,hy)=>{if(t>=9.95)quietHead(hx,hy,t);}};
 const b=figure(2,760,B,t);if(t>=9.95)pictureBubbles(b.hx,b.hy,t);
 // A's words
 for(let i=0;i<BUB.length;i++)bubble(i,BUB[i],a.hx,a.hy,t);swatBurst(a.hx,a.hy,t);
 if(t>=10.2&&t<17.9)wordStream(a.hx,a.hy,t,10.2);
 if(!silent)motes(cam,t);
 g.setTransform(1,0,0,1,0,0);const v=g.createRadialGradient(W/2,H*.48,H*.25,W/2,H*.5,H*.78);v.addColorStop(0,'rgba(5,14,30,0)');v.addColorStop(1,'rgba(5,14,30,.55)');g.fillStyle=v;g.fillRect(0,0,W,H);
 if(silent){g.fillStyle='rgba(5,14,30,.28)';g.fillRect(0,0,W,H);}
 const fl=t>=10&&t<10.2?.13*(1-(t-10)/.2):0;if(fl>0){g.fillStyle=`rgba(159,240,226,${fl})`;g.fillRect(0,0,W,H);}
 overlay(t);}

const GR=document.createElement('canvas');GR.width=GR.height=256;{const c=GR.getContext('2d'),d=c.createImageData(256,256),r=mul(5);for(let i=0;i<d.data.length;i+=4){const v=r()*255;d.data[i]=d.data[i+1]=d.data[i+2]=v;d.data[i+3]=10;}c.putImageData(d,0,0);}
window.renderAt=function(t){
 const c0=camAt(t),c1=camAt(t+1/60);let sp=Math.hypot((c1[0]-c0[0])*c0[2],(c1[1]-c0[1])*c0[2])+Math.abs(Math.log(c1[2]/c0[2]))*900;if(Math.abs(t-SNAP)<1/60)sp=0;
 const S=sp>18?5:sp>7?3:1;out.setTransform(1,0,0,1,0,0);
 for(let k=0;k<S;k++){scene(t+(S>1?(k/(S-1)-.5)/60:0));out.globalAlpha=1/(k+1);out.drawImage(buf,0,0);}
 out.globalAlpha=1;const r=Math.floor(t*30);out.drawImage(GR,-(r*37%256),-(r*91%256),W+512,H+512);
 return cv.toDataURL('image/jpeg',.93);};
document.fonts.load(`64px ${MARK}`).then(()=>document.fonts.load(`bold 40px ${MONO}`)).then(()=>{window.ready=true;});
