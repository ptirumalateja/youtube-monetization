// Sleep paralysis reel v3: chalk-on-black stickman horror. Canvas 2D, every frame a pure function of t.
const W=1080,H=1920;
const cv=document.getElementById('c');cv.width=W;cv.height=H;const g=cv.getContext('2d');
const CHALK='#ecebe4',DIM='rgba(236,235,228,.55)',MOON='#9cc3e6',BLOOD='#d3141c',INK='#040507';

// ---------- timing (overwritten from timeline.json when voiceover timestamps exist) ----------
let TL=window.TL||{
 dur:20,
 beats:{wake:0,eyes:.45,something:2.7,figure:3.0,isSP:5.2,brain:7.0,locked:8.7,spill:10.6,see:13.0,stat:15.0,back:18.4,end:20},
 captions:[[.15,1.2,'YOU WAKE UP...'],[1.25,2.6,"BUT YOU CAN'T MOVE."],[2.65,4.9,'AND SOMETHING IS STANDING IN YOUR ROOM.'],[5.1,6.9,'THIS IS SLEEP PARALYSIS.'],
  [7.0,8.6,'YOUR BRAIN WAKES UP,'],[8.6,10.5,'BUT YOUR BODY IS STILL LOCKED IN DREAM SLEEP.'],[10.6,12.8,'SO THE DREAM SPILLS INTO YOUR BEDROOM.'],[13.0,14.9,'SOME PEOPLE EVEN SEE A FIGURE.'],[15.0,18.3,'NEARLY 1 IN 10 PEOPLE WILL FEEL THIS AT LEAST ONCE.']],
};
window.setTL=x=>{TL=x;};
const VO_OFFSET=.35;
async function loadTL(){try{const d=await (await fetch('audio/vo_timestamps.json')).json();const o=VO_OFFSET,w=d.words.map(x=>({...x,start:x.start+o,end:x.end+o}));
 const at=(word,n=0)=>w.filter(x=>x.word.toLowerCase().replace(/[^a-z']/g,'')===word)[n].start;
 const caps=[];for(const sg of d.segments){const ws=sg.words.map(x=>x.start+o);caps.push([sg.start+o-.05,0,sg.text.toUpperCase().replace('…','...'),ws]);}
 caps.forEach((c,i)=>{c[1]=i<caps.length-1?caps[i+1][0]-.02:Math.min(19.75,d.duration+o+.25);});
 TL={dur:20,captions:caps,beats:{wake:0,eyes:at('up')-.05,something:at('something'),figure:at('standing'),isSP:at('this'),brain:at('brain'),locked:at('body'),spill:at('so'),see:at('some'),stat:at('nearly'),back:Math.max(at('once')-.1,18.75),end:20}};
 window.TLsrc='vo';}catch(e){window.TLsrc='default';}}


// ---------- deterministic randomness with a 10 fps "boil" ----------
function mul(a){return()=>{a|=0;a=a+0x6D2B79F5|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return((t^t>>>14)>>>0)/4294967296;};}
let rnd=Math.random,BOILF=0;
const seed=s=>{rnd=mul(s*7919+BOILF*104729);};
const J=(a)=>(rnd()-.5)*2*a;
const clamp=(x,a=0,b=1)=>Math.min(b,Math.max(a,x)),lerp=(a,b,t)=>a+(b-a)*t,ease=t=>t<.5?4*t*t*t:1-Math.pow(-2*t+2,3)/2,ss=(a,b,x)=>{const t=clamp((x-a)/(b-a));return t*t*(3-2*t);};
const seg=(t,a,b)=>clamp((t-a)/(b-a));

// ---------- chalk primitives ----------
let ZOOM=1;
function wob(pts,amp){const out=[];for(let i=0;i<pts.length-1;i++){const [x0,y0]=pts[i],[x1,y1]=pts[i+1];const L=Math.hypot(x1-x0,y1-y0),n=Math.max(1,Math.round(L/28));
  for(let k=0;k<n;k++){const u=k/n;out.push([lerp(x0,x1,u)+J(amp),lerp(y0,y1,u)+J(amp)]);}}
 const l=pts[pts.length-1];out.push([l[0]+J(amp),l[1]+J(amp)]);return out;}
function path(p,closed){g.beginPath();g.moveTo(p[0][0],p[0][1]);for(let i=1;i<p.length-1;i++){const mx=(p[i][0]+p[i+1][0])/2,my=(p[i][1]+p[i+1][1])/2;g.quadraticCurveTo(p[i][0],p[i][1],mx,my);}const l=p[p.length-1];g.lineTo(l[0],l[1]);if(closed)g.closePath();}
// several loose passes of a chalk stroke with glow; `reveal` draws only the first fraction (stroke-on animation)
function chalk(pts,o={}){const w=(o.w||3.2)/Math.sqrt(ZOOM)*1.0,col=o.col||CHALK,passes=o.passes||2,amp=(o.amp??2.2);let P=pts;
 if(o.reveal!==undefined&&o.reveal<1){if(o.reveal<=0)return;P=partial(pts,o.reveal);}
 g.save();g.lineCap='round';g.lineJoin='round';g.strokeStyle=col;g.shadowColor=o.glowCol||col;g.shadowBlur=(o.glow??7);
 for(let k=0;k<passes;k++){g.globalAlpha=(o.alpha??1)*(k?.55:1);g.lineWidth=w*(k?.6:1);path(wob(P,amp*(k?1.4:1)),o.closed);g.stroke();}
 g.restore();}
function partial(pts,f){let L=0;const d=[0];for(let i=1;i<pts.length;i++){L+=Math.hypot(pts[i][0]-pts[i-1][0],pts[i][1]-pts[i-1][1]);d.push(L);}const T=L*f,out=[pts[0]];
 for(let i=1;i<pts.length;i++){if(d[i]<=T)out.push(pts[i]);else{const u=(T-d[i-1])/(d[i]-d[i-1]);out.push([lerp(pts[i-1][0],pts[i][0],u),lerp(pts[i-1][1],pts[i][1],u)]);break;}}return out.length<2?[pts[0],pts[0]]:out;}
function circ(cx,cy,rx,ry,n=24,rot=0){const p=[];for(let i=0;i<=n;i++){const a=rot+i/n*Math.PI*2;p.push([cx+Math.cos(a)*rx,cy+Math.sin(a)*ry]);}return p;}
function fillPoly(p,col=INK){g.save();g.fillStyle=col;g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p)g.lineTo(q[0],q[1]);g.closePath();g.fill();g.restore();}
// diagonal scribble hatching clipped to a polygon (the reference's chalk-shaded blocks)
function hatch(p,o={}){const xs=p.map(q=>q[0]),ys=p.map(q=>q[1]);const x0=Math.min(...xs),x1=Math.max(...xs),y0=Math.min(...ys),y1=Math.max(...ys);
 g.save();g.beginPath();g.moveTo(p[0][0],p[0][1]);for(const q of p)g.lineTo(q[0],q[1]);g.closePath();g.clip();g.strokeStyle=o.col||CHALK;g.lineCap='round';
 const sp=o.sp||16,ang=o.ang??-1.1,dx=Math.cos(ang),dy=Math.sin(ang);const n=Math.ceil((x1-x0+y1-y0)/sp);
 for(let i=0;i<n*(o.dens||1);i++){const x=x0+rnd()*(x1-x0),y=y0+rnd()*(y1-y0),l=(o.len||40)*(.4+rnd());g.globalAlpha=(o.alpha||.35)*(.3+rnd()*.7);g.lineWidth=(o.lw||1.6)*(.6+rnd()*.8);
  g.beginPath();g.moveTo(x,y);g.lineTo(x+dx*l,y+dy*l);g.stroke();}
 g.restore();}
function grass(x,y,s=1){for(let i=0;i<9;i++){const a=-Math.PI/2+J(.9),l=(14+rnd()*26)*s;chalk([[x+J(10*s),y],[x+Math.cos(a)*l*.5,y+Math.sin(a)*l*.6],[x+Math.cos(a)*l,y+Math.sin(a)*l]],{w:1.6,amp:.6,passes:1,glow:5});}}
function block(x0,y0,x1,y1,o={}){const p=[[x0,y0],[x1,y0],[x1,y1],[x0,y1]];fillPoly(p);hatch(p,{sp:12,len:60,alpha:.33,...o});chalk([[x0,y1],[x0,y0],[x1,y0],[x1,y1]],{w:3.4});}

// ---------- characters ----------
// The kid lying in bed (head on the pillow at hx,hy, facing up/right). pupils look toward (lx,ly).
function kid(hx,hy,s,st){
 const r=58*s;
 // hair spikes behind the head
 for(let i=0;i<22;i++){const a=Math.PI*.55+i/21*Math.PI*1.05+J(.08);const l=r*(1.05+rnd()*.5);chalk([[hx+Math.cos(a)*r*.7,hy+Math.sin(a)*r*.7],[hx+Math.cos(a+J(.15))*l,hy+Math.sin(a+J(.15))*l]],{w:2,amp:1,passes:1,glow:6});}
 fillPoly(circ(hx,hy,r,r*1.02,28));chalk(circ(hx,hy,r,r*1.02,22),{w:3.2,closed:true});
 // eyes: closed lines -> huge white circles; tremble when terrified
 const open=st.eyes,tr=st.tremble||0;const ex=hx+r*.05+J(tr*2),ey=hy-r*.18+J(tr*2);
 for(const [dx,dy] of [[-.38,-.02],[.36,.05]]){const cx=ex+dx*r,cy=ey+dy*r;
  if(open<.08){chalk([[cx-r*.2,cy],[cx,cy+r*.06],[cx+r*.2,cy]],{w:2.6,amp:.5,passes:1});continue;}
  const er=r*.34*(.6+.4*open);g.save();g.fillStyle=CHALK;g.shadowColor=CHALK;g.shadowBlur=10;g.beginPath();g.ellipse(cx,cy,er,er*open,0,0,7);g.fill();g.restore();
  const px=clamp((st.lx-cx)/600,-1,1)*er*.42,py=clamp((st.ly-cy)/600,-1,1)*er*.42*open;g.fillStyle=INK;g.beginPath();g.ellipse(cx+px+J(tr*1.5),cy+py+J(tr*1.5),er*.45,er*.45*Math.max(.4,open),0,0,7);g.fill();
  // red veins appear when panic peaks
  if(st.veins>0){for(let k=0;k<4;k++){const a=rnd()*7;chalk([[cx+Math.cos(a)*er*.95,cy+Math.sin(a)*er*.95*open],[cx+Math.cos(a)*er*.55,cy+Math.sin(a)*er*.55*open]],{w:1.4,col:BLOOD,amp:.6,passes:1,glow:4,alpha:st.veins});}}}
 // mouth: small open "o" of fear
 const m=st.mouth||0;if(m>0){g.save();g.strokeStyle=CHALK;g.lineWidth=2.4;g.beginPath();g.ellipse(hx+r*.05,hy+r*.45,r*.09*(.6+m*.4),r*.13*m+2,0,0,7);g.stroke();g.restore();}
 else chalk([[hx-r*.12,hy+r*.45],[hx+r*.14,hy+r*.43]],{w:2,passes:1,amp:.6});
 // sweat drop
 if(st.sweat>0){const sy=hy-r*.5+st.sweat*r*.9;chalk(circ(hx+r*.95,sy,6,9,10),{w:2,closed:true,alpha:clamp(1-st.sweat*.6)});}
}
// bed with pillow, blanket, the body shape underneath, and a gripping hand
function bed(x,y,s,st){ // x,y = left foot of the bed on the floor
 const L=620*s,top=y-125*s;
 chalk([[x,y],[x,y-330*s]],{w:4});chalk([[x+L,y],[x+L,y-200*s]],{w:4});chalk([[x-6*s,y-330*s],[x+10*s,y-345*s],[x+26*s,y-330*s]],{w:3});
 const frame=[[x,top],[x+L,top],[x+L,top+40*s],[x,top+40*s]];fillPoly(frame);hatch(frame,{sp:10,len:30,alpha:.25});chalk([[x,top],[x+L,top],[x+L,top+40*s],[x,top+40*s]],{w:3,closed:true});
 for(const lx of [x+20*s,x+L-20*s])chalk([[lx,top+40*s],[lx,y]],{w:3});
 // pillow
 const pw=[[x+25*s,top-5*s],[x+30*s,top-55*s],[x+170*s,top-62*s],[x+190*s,top-8*s]];fillPoly(pw);chalk(pw,{w:3,closed:true});
 // blanket over the body: chest heaves, a failed attempt to lift lifts the hump slightly
 const br=Math.sin(st.t*6.5)*4*s*(st.panic||0),att=st.attempt||0;
 const bl=[[x+150*s,top-8*s],[x+170*s,top-70*s-br],[x+260*s,top-92*s-br-att*14*s],[x+360*s,top-70*s],[x+450*s,top-58*s],[x+560*s,top-74*s],[x+600*s,top-40*s],[x+L+15*s,top+8*s],[x+L+10*s,top+60*s],[x+140*s,top+58*s]];
 fillPoly(bl);hatch(bl,{sp:9,len:34,alpha:.28,ang:-.6});chalk(bl,{w:3.4,closed:true});
 // fold lines
 chalk([[x+300*s,top-70*s],[x+330*s,top+20*s]],{w:1.8,passes:1,alpha:.7});chalk([[x+480*s,top-58*s],[x+470*s,top+30*s]],{w:1.8,passes:1,alpha:.7});
 // hand gripping the blanket edge: fingers twitch but never lift
 const hx=x+235*s,hy=top-80*s-br-att*10*s;for(let f=0;f<4;f++){const fx=hx+f*13*s,tw=Math.sin(st.t*23+f*2)*3*s*(st.twitch||0);chalk([[fx,hy+4*s],[fx+2*s,hy-14*s-tw]],{w:2.4,amp:.5,passes:1});}
 chalk(circ(hx+20*s,hy+10*s,26*s,12*s,12),{w:2.6,closed:true});
 return {head:[x+105*s,top-62*s]};
}
// the figure: a tall thin shadow of tangled branches, red ember eyes, long claws
function figure(x,y,s,st){ // x,y = feet on the floor
 const lean=st.lean||0,h=760*s,a=st.alpha??1;if(a<=0)return;g.save();g.globalAlpha=a;
 const hip=[x,y-h*.48],neck=[x-lean*170*s,y-h*.9+lean*40*s],head=[neck[0]-lean*120*s-30*s,neck[1]-55*s+lean*70*s];
 // body silhouette
 const body=[[x-34*s,y],[x-26*s,y-h*.25],[x-30*s,hip[1]],[x-70*s,hip[1]-150*s],[neck[0]-95*s,neck[1]+40*s],[neck[0]-40*s,neck[1]-6*s],[neck[0]+40*s,neck[1]-10*s],[neck[0]+90*s,neck[1]+30*s],[x+72*s,hip[1]-140*s],[x+30*s,hip[1]],[x+28*s,y-h*.25],[x+40*s,y]];
 fillPoly(body,'#000');hatch(body,{sp:6,len:30,alpha:.22,col:'#cfcac0',ang:-1.25,dens:1.4});hatch(body,{sp:9,len:22,alpha:.25,col:BLOOD,ang:-.4});
 chalk(body,{w:3.2,col:'#d9d5cb',glowCol:BLOOD,glow:14,closed:true,amp:5});chalk(body,{w:1.6,col:BLOOD,glow:6,closed:true,amp:8,passes:1});
 // legs dissolve into roots
 for(let i=0;i<12;i++){const sx=x+J(24*s);chalk([[sx,y-6],[sx+J(60*s),y+4*s],[sx+J(120*s),y+J(6*s)]],{w:1.8,col:i%3?'#d9d5cb':BLOOD,glow:6,passes:1,amp:2});}
 // arms: shoulder -> elbow -> wrist, claws
 const arms=[];for(const sd of [-1,1]){const sh=[neck[0]+sd*82*s,neck[1]+34*s];const reach=sd<0?st.reach||0:0;
  const el=[sh[0]+sd*34*s-reach*130*s-lean*40*s,sh[1]+230*s-reach*110*s],wr=[el[0]+sd*10*s-reach*150*s,el[1]+220*s-reach*30*s];
  chalk([sh,el,wr],{w:16*s+2,col:'#000',glow:0,passes:1,amp:1});chalk([[sh[0]-7*s,sh[1]],[el[0]-6*s,el[1]],[wr[0]-4*s,wr[1]]],{w:2.6,col:'#d9d5cb',glowCol:BLOOD,glow:10,amp:2.4});chalk([[sh[0]+7*s,sh[1]],[el[0]+6*s,el[1]],[wr[0]+4*s,wr[1]]],{w:2.6,col:'#d9d5cb',glowCol:BLOOD,glow:10,amp:2.4});
  for(let f=0;f<4;f++){const ang=Math.PI/2+(f-1.5)*.28-reach*.9*(sd<0?1:0)+(st.claw||0)*.3;const l=(95+f*8)*s;const mid=[wr[0]+Math.cos(ang)*l*.55,wr[1]+Math.sin(ang)*l*.55],tip=[wr[0]+Math.cos(ang+.25*(st.claw||0))*l,wr[1]+Math.sin(ang+.25*(st.claw||0))*l];
   chalk([wr,mid,tip],{w:2.2,col:CHALK,glow:6,amp:1,passes:1,alpha:.75});}arms.push(wr);}
 // head: long dark skull, branch crown, ember eyes
 fillPoly(circ(head[0],head[1],78*s,104*s,22,lean*.5),'#000');hatch(circ(head[0],head[1],78*s,104*s,22,lean*.5),{sp:6,len:20,alpha:.18,col:'#cfcac0',ang:-1.2});chalk(circ(head[0],head[1],78*s,104*s,18,lean*.5),{w:3.2,col:'#d9d5cb',glowCol:BLOOD,glow:14,closed:true,amp:3});
 const crown=st.crown??1;for(let i=0;i<18;i++){const a=-Math.PI/2+(i-8.5)*.17+J(.05);const l=(170+((i*37)%11)*22)*s*crown;const p0=[head[0]+Math.cos(a)*60*s,head[1]+Math.sin(a)*85*s];
  const p1=[p0[0]+Math.cos(a)*l*.5+J(14),p0[1]+Math.sin(a)*l*.5],p2=[p0[0]+Math.cos(a+J(.3))*l,p0[1]+Math.sin(a+J(.3))*l];chalk([p0,p1,p2],{w:3,col:'#cfcac0',glow:6,passes:1,amp:2});
  if(i%2===0)chalk([p1,[p1[0]+Math.cos(a+.6)*l*.35,p1[1]+Math.sin(a+.6)*l*.35]],{w:2,col:'#cfcac0',glow:4,passes:1,amp:1});chalk([p2,[p2[0]+Math.cos(a-.5)*l*.25,p2[1]+Math.sin(a-.5)*l*.25]],{w:1.6,col:i%5===0?BLOOD:'#cfcac0',glow:4,passes:1,amp:1});}
 const e=st.eyes??1;if(e>0){for(const dx of [-.42,.3]){const ex=head[0]+dx*70*s-lean*20*s,ey=head[1]-4*s+lean*10*s;const gr=g.createRadialGradient(ex,ey,0,ex,ey,48*s*e);gr.addColorStop(0,'rgba(255,90,80,'+e+')');gr.addColorStop(.25,'rgba(211,20,28,'+e*.9+')');gr.addColorStop(1,'rgba(211,20,28,0)');
  g.fillStyle=gr;g.beginPath();g.arc(ex,ey,48*s*e,0,7);g.fill();g.fillStyle='rgba(255,215,205,'+e+')';g.beginPath();g.ellipse(ex,ey,11*s,6*s,-.2,0,7);g.fill();}}
 g.restore();return {head,hand:arms[0]};
}
function windowMoon(x,y,s,lit=1){ // floating window frame with moon and bare branch, and a cold moon beam
 const w=230*s,h=320*s;
 g.save();const gr=g.createLinearGradient(x,y,x+w*1.5,y+h*3.2);gr.addColorStop(0,`rgba(156,195,230,${.16*lit})`);gr.addColorStop(1,'rgba(156,195,230,0)');g.fillStyle=gr;g.beginPath();g.moveTo(x,y+h);g.lineTo(x+w,y+h);g.lineTo(x+w*1.6,y+h*3.1);g.lineTo(x+w*.15,y+h*3.1);g.closePath();g.fill();g.restore();
 g.save();g.fillStyle=`rgba(156,195,230,${.95*lit})`;g.shadowColor=MOON;g.shadowBlur=40;g.beginPath();g.arc(x+w*.62,y+h*.34,48*s,0,7);g.fill();g.restore();
 chalk([[x+w*.1,y+h],[x+w*.3,y+h*.6],[x+w*.25,y+h*.3],[x+w*.5,y+h*.12]],{w:2.4,col:'#0a0c10',glow:0,passes:1});
 const fr=[[x,y],[x+w,y],[x+w,y+h],[x,y+h]];chalk(fr,{w:3.6,closed:true});chalk([[x+w/2,y],[x+w/2,y+h]],{w:3});chalk([[x,y+h/2],[x+w,y+h/2]],{w:3});
}
// brain-awake / body-locked explainer
function brainBubble(cx,cy,s,f){ if(f<=0)return; const pts=[];for(let i=0;i<=40;i++){const a=i/40*Math.PI*2;const r=1+.13*Math.sin(a*7);pts.push([cx+Math.cos(a)*230*s*r,cy+Math.sin(a)*150*s*r]);}
 fillPoly(pts);chalk(pts,{w:3.4,closed:true,reveal:f*1.6});
 for(const [dx,dy,r] of [[-120,190,22],[-160,250,13]])chalk(circ(cx+dx*s,cy+dy*s,r*s,r*s,12),{w:2.6,closed:true,reveal:f*2-.3});
 if(f>.35){const b=clamp((f-.35)/.4);const br=circ(cx,cy,120*s,82*s,30);chalk(br,{w:3,closed:true,reveal:b,col:CHALK});
  for(let i=0;i<6;i++){const yy=cy-50*s+i*20*s;chalk([[cx-95*s,yy],[cx-40*s,yy+J(12)],[cx+10*s,yy-8*s],[cx+60*s,yy+J(12)],[cx+95*s,yy]],{w:1.8,passes:1,alpha:.8*b,amp:4});}
  chalk([[cx,cy-80*s],[cx,cy+80*s]],{w:2,alpha:b});
  // awake: lightning sparks around the brain
  for(let i=0;i<8;i++){const a=i/8*Math.PI*2+BOILF*.1;chalk([[cx+Math.cos(a)*140*s,cy+Math.sin(a)*100*s],[cx+Math.cos(a)*170*s+J(8),cy+Math.sin(a)*120*s+J(8)],[cx+Math.cos(a)*195*s,cy+Math.sin(a)*140*s]],{w:2,alpha:b,col:MOON,glowCol:MOON,glow:10,passes:1});}}
}
function chains(x,y,s,f){ if(f<=0)return; // chain links wrap the blanket, then a padlock snaps shut
 for(const yy of [-40,10]){const n=11;for(let i=0;i<n;i++){const u=i/(n-1);if(u>f*1.25)break;const cx=x+150*s+u*480*s,cy=y+yy*s+Math.sin(u*9)*6*s;chalk(circ(cx,cy,24*s,13*s,12,i%2?0:.0),{w:2.6,closed:true,glow:8});}}
 const p=clamp((f-.75)/.25);if(p>0){const lx=x+400*s,ly=y-10*s;g.save();g.globalAlpha=p;const body=[[lx-34*s,ly],[lx+34*s,ly],[lx+34*s,ly+56*s],[lx-34*s,ly+56*s]];fillPoly(body);chalk(body,{w:3,closed:true,col:BLOOD,glowCol:BLOOD,glow:12});
  const sh=(1-p)*18*s;chalk([[lx-20*s,ly],[lx-20*s,ly-30*s-sh],[lx,ly-48*s-sh],[lx+20*s,ly-30*s-sh],[lx+20*s,ly-sh]],{w:3,col:BLOOD,glowCol:BLOOD,glow:12});chalk(circ(lx,ly+26*s,6*s,8*s,10),{w:2,closed:true,col:BLOOD});g.restore();}
}
function dreamSmoke(from,to,f,t){ if(f<=0)return; // scribble smoke pours out of a dream cloud and crawls to the figure
 for(let k=0;k<40;k++){const ph=(k/26+t*.35)%1;const u=Math.min(ph,f);const x=lerp(from[0],to[0],u)+Math.sin(u*9+k)*60*(1-u)+J(6),y=lerp(from[1],to[1],u)-Math.sin(u*Math.PI)*260+Math.cos(u*7+k)*40;
  chalk(circ(x,y,(26+k%5*9)*(1-u*.4),(18+k%3*8)*(1-u*.4),10,k),{w:2.6,col:k%6===0?BLOOD:CHALK,glow:10,passes:1,amp:4,alpha:.85*(1-u*.3)});}
}
function cloud(cx,cy,s,f){if(f<=0)return;const pts=[];for(let i=0;i<=36;i++){const a=i/36*Math.PI*2;const r=1+.18*Math.abs(Math.sin(a*4));pts.push([cx+Math.cos(a)*150*s*r,cy+Math.sin(a)*90*s*r]);}fillPoly(pts);chalk(pts,{w:3,closed:true,reveal:f*1.5});
 for(const [dx,dy,r] of [[-60,120,16],[-85,160,9]])chalk(circ(cx+dx*s,cy+dy*s,r*s,r*s,10),{w:2.2,closed:true,reveal:f*2-.4});}

// ---------- world ----------
const FLOOR=1250;
function room(ox,oy,s,st,isOurs){ // one bedroom resting on a floating chalk block
 g.save();g.translate(ox,oy);g.scale(s,s);
 windowMoon(420,560,1,st.moon??1);
 block(-120,FLOOR,1420,FLOOR+520);grass(-60,FLOOR,1);grass(1300,FLOOR,1.1);grass(980,FLOOR,.8);
 const B=bed(150,FLOOR,1,st);
 // door outline, ajar, faint light gap
 chalk([[1180,FLOOR],[1180,760],[1360,760],[1360,FLOOR]],{w:3,alpha:.8});g.save();g.fillStyle='rgba(236,235,228,.08)';g.fillRect(1182,762,30,FLOOR-762);g.restore();chalk([[1212,FLOOR-4],[1212,770]],{w:2,alpha:.6});
 const out={head:B.head};
 if(isOurs&&st.fig){out.fig=figure(st.fig.x,FLOOR,st.fig.s||1,st.fig);}
 kid(B.head[0],B.head[1],1,st.kid);
 g.restore();return out;
}

// ---------- camera keys: [t, cx, cy, zoom] (world coordinates of frame centre) ----------
function camAt(t,b){const K=[[0,330,1060,2.3],[b.eyes+.35,290,1075,2.75],[b.eyes+1.3,300,1070,2.6],[b.something-.1,380,1030,1.9],[b.figure+.6,760,960,1.0],[b.isSP-.2,700,980,1.05],[b.isSP+.5,300,1060,3.0],[b.brain,330,1000,1.45],[b.locked+1,420,1030,1.35],[b.spill+.4,640,950,1.0],[b.see-.1,620,880,1.05],[b.see+1.3,520,860,1.6],[b.stat+.2,560,1020,1.25],[b.stat+1.3,1500,1900,.33],[b.back-.2,1500,1900,.32],[b.back+.9,330,1060,2.3],[b.end,330,1060,2.3]];
 let i=0;while(i<K.length-2&&t>K[i+1][0])i++;const [t0,x0,y0,z0]=K[i],[t1,x1,y1,z1]=K[i+1];const u=ease(clamp((t-t0)/(t1-t0)));
 return [lerp(x0,x1,u),lerp(y0,y1,u),Math.exp(lerp(Math.log(z0),Math.log(z1),u))];}

// ten rooms for the "1 in 10" beat: ours is index 6 at the world origin
const GRID=[];for(let r=0;r<5;r++)for(let c=0;c<2;c++)GRID.push([c*1600-0,r*1050-2*1050]);
const OURS=6;const OFF=GRID[OURS];

function caption(t){const c=TL.captions.find(([a,b])=>t>=a&&t<b);if(!c)return;const [a,b,txt]=c;const p=clamp((t-a)/.12),q=clamp((b-t)/.1);
 g.save();g.font='bold 66px "Chalkboard SE", "Chalkboard", sans-serif';g.textAlign='center';g.textBaseline='middle';
 const words=txt.split(' '),lines=[];let cur='';for(const w of words){const tr=cur?cur+' '+w:w;if(g.measureText(tr).width>900){lines.push(cur);cur=w;}else cur=tr;}lines.push(cur);
 const y0=1600-(lines.length-1)*40;{const pad=g.createRadialGradient(W/2,1600,40,W/2,1600,560);pad.addColorStop(0,'rgba(0,0,0,.85)');pad.addColorStop(1,'rgba(0,0,0,0)');g.save();g.globalAlpha=Math.min(p,q);g.fillStyle=pad;g.fillRect(0,1300,W,600);g.restore();}g.globalAlpha=Math.min(p,q);const sc=.9+.1*ease(p);g.translate(W/2,y0);g.scale(sc,sc);
 // words reveal in time with the line; the key words go blood red
 const hot=/SOMETHING|PARALYSIS|LOCKED|DREAM|FIGURE|1|10/;
 let shown=c[3]?c[3].filter(ws=>t>=ws-.03).length:Math.ceil(words.length*clamp((t-a)/Math.max(.4,(b-a)*.75)));let k=0;
 lines.forEach((ln,li)=>{const ws=ln.split(' ');let x=-g.measureText(ln).width/2;ws.forEach(w=>{const ww=g.measureText(w+' ').width;if(k<shown){g.lineWidth=12;g.strokeStyle='#000';g.lineJoin='round';g.strokeText(w,x+g.measureText(w).width/2,li*80);g.fillStyle=hot.test(w.replace(/[^A-Z0-9]/g,''))?'#ff2a2f':CHALK;g.shadowColor=g.fillStyle;g.shadowBlur=8;g.fillText(w,x+g.measureText(w).width/2,li*80);g.shadowBlur=0;}x+=ww;k++;});});
 g.restore();}
function title(t){const fo=1-ss(TL.beats.see-.4,TL.beats.see,t);if(fo<=0)return;g.save();g.globalAlpha=fo;g.font='86px "Chalkduster", "Chalkboard SE", sans-serif';g.textAlign='center';g.textBaseline='middle';
 const shake=t<.35?(1-t/.35)*10:0;const k=ss(2.7,3.3,t);g.translate(W/2+J(shake),lerp(250,150,k)+J(shake));const sc=(t<.25?1.25-.25*ease(t/.25):1)*lerp(1,.6,k);g.scale(sc,sc);
 g.fillStyle=CHALK;g.shadowColor=CHALK;g.shadowBlur=14;g.fillText('SLEEP',0,-52);g.fillStyle='#ff2a2f';g.shadowColor=BLOOD;g.shadowBlur=18;g.fillText('PARALYSIS',0,44);g.restore();
 {const k=ss(2.7,3.3,t),yy=lerp(345,207,k),hw=lerp(250,150,k);chalk([[W/2-hw,yy],[W/2-hw*.25,yy+7],[W/2+hw,yy-3]],{w:3,col:BLOOD,glow:10,passes:1,alpha:fo});}}

window.renderAt=function(t){
 const b=TL.beats;BOILF=Math.floor(t*10);
 g.setTransform(1,0,0,1,0,0);g.fillStyle=INK;g.fillRect(0,0,W,H);
 // stage state
 const panic=ss(b.eyes,b.eyes+.4,t);
 const figAppear=ss(b.something,b.figure+.3,t);
 const toBed=ss(b.spill+.3,b.see+.2,t); // figure glides from the doorway to the bedside, fed by the dream smoke
 const fig={x:lerp(1000,830,toBed),s:1,lean:ss(b.see-.2,b.see+1.4,t)*.9,reach:ss(b.see,b.stat-.2,t),claw:ss(b.stat-1,b.stat,t),eyes:ss(b.something+.2,b.figure+.2,t)*(1-ss(b.isSP+.4,b.isSP+.6,t)*0)+0,alpha:figAppear,crown:.6+.4*ss(b.figure,b.see,t)};
 const ks={eyes:ss(b.eyes,b.eyes+.12,t),lx:fig.x,ly:700,tremble:panic*(1+ss(b.see,b.see+1,t)*1.5),mouth:ss(b.figure,b.figure+.4,t),veins:ss(b.see,b.see+1,t),sweat:t>b.isSP?((t-b.isSP)*.6)%1:0};
 if(t<b.figure)ks.lx=200,ks.ly=700; // stares at the ceiling until it notices
 const st={t,panic,attempt:Math.max(0,Math.sin((t-b.wake)*5))*ss(b.wake+.8,b.wake+1.3,t)*(1-ss(b.something,b.something+.4,t)),twitch:panic,kid:ks,fig,moon:1-.35*ss(b.spill,b.see,t)};
 const [cx,cy,z]=camAt(t,b);ZOOM=z;
 // slow handheld drift + tension shake near the climax
 const sh=ss(b.see+.6,b.stat,t)*(1-ss(b.stat,b.stat+.4,t))*6+Math.max(0,1-Math.abs(t-(b.eyes+1.1))/.35)*7;
 g.setTransform(z,0,0,z,W/2-cx*z+J(sh),H/2-cy*z+J(sh));
 // other rooms (only visible when zoomed out)
 if(z<.9){GRID.forEach((o,i)=>{if(i===OURS)return;seed(100+i);room(o[0]-OFF[0],o[1]-OFF[1],1,{t:t+i*.37,kid:{eyes:0,lx:0,ly:0},moon:1},false);});}
 seed(7);const R=room(0,0,1,st,true);
 // explainer layers in world space above our bed
 seed(11);if(t>b.brain-.1&&t<b.spill+.5){const f=ss(b.brain-.1,b.brain+.6,t)*(1-ss(b.spill+.1,b.spill+.5,t));brainBubble(330,770,.85,f);chains(150,1105,1,ss(b.locked,b.locked+1.2,t)*(1-ss(b.spill+.1,b.spill+.5,t)));}
 seed(13);if(t>b.spill-.1&&t<b.see+.6){const f=ss(b.spill-.1,b.spill+.4,t)*(1-ss(b.see+.1,b.see+.6,t));cloud(360,800,.9,f);dreamSmoke([440,800],[fig.x-30,560],ss(b.spill+.2,b.see,t)*f,t);}
 // screen space: "1 IN 10" stamp, title, captions, vignette, grain
 g.setTransform(1,0,0,1,0,0);
 if(t>b.stat+.8&&t<b.back+.2){const f=ss(b.stat+.8,b.stat+1.1,t)*(1-ss(b.back-.1,b.back+.2,t));seed(21);g.save();g.globalAlpha=f;g.font='bold 170px "Chalkboard SE", sans-serif';g.textAlign='center';g.textBaseline='middle';g.lineWidth=16;g.strokeStyle='#000';g.strokeText('1 IN 10',W/2,1330);g.fillStyle='#ff2a2f';g.shadowColor=BLOOD;g.shadowBlur=24;g.fillText('1 IN 10',W/2,1330);g.restore();
  // a chalk ring around our room
  const [rx,ry]=[W/2+(650-cx)*z,H/2+(1050-cy)*z];chalk(circ(rx,ry,1000*z*.8,700*z*.8,30,BOILF*.02),{w:4,col:BLOOD,glowCol:BLOOD,glow:14,closed:true,reveal:f});}
 const vg=g.createRadialGradient(W/2,H*.52,H*.25,W/2,H*.52,H*.75);vg.addColorStop(0,'rgba(0,0,0,0)');vg.addColorStop(1,'rgba(0,0,0,.75)');g.fillStyle=vg;g.fillRect(0,0,W,H);
 seed(3);title(t);caption(t);
 // brief black blink at the loop seam
 const bl=Math.max(ss(b.end-.18,b.end,t),1-ss(0,.08,t));if(bl>0){g.fillStyle=`rgba(0,0,0,${bl})`;g.fillRect(0,0,W,H);}
 return cv.toDataURL('image/jpeg',.92);
};
loadTL().then(()=>document.fonts.load('86px "Chalkduster"')).then(()=>document.fonts.load('bold 66px "Chalkboard SE"')).then(()=>{window.renderAt(+(new URLSearchParams(location.search).get('t')||3));window.ready=true;});
