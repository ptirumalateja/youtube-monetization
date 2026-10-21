// 2D layer drawn over the graded frame: the SLEEP PARALYSIS title, word-synced captions, and the eyes in the final black.
const KEY=new Set(["3","a.m.","can't","scream","something","corner","sleep","paralysis","asleep","trapped","closer","don't","eyes"]);
const isKey=w=>{const n=w.toLowerCase().replace(/[^a-z0-9.']/g,'');return KEY.has(n==='a.m.'?n:n.replace(/\.+$/,''));};
const sm=(a,b,x)=>{const t=Math.min(1,Math.max(0,(x-a)/(b-a)));return t*t*(3-2*t);};
function rng(s){return()=>{s=(s*1664525+1013904223)>>>0;return s/4294967296;};}

// the title is drawn once, then distressed (chipped, scratched) so it reads like an old horror one-sheet
function titleCanvas(){const c=document.createElement('canvas');c.width=1000;c.height=420;const x=c.getContext('2d');x.textAlign='center';x.textBaseline='alphabetic';
 x.fillStyle='#e6dfcc';x.font='900 178px Cinzel';x.letterSpacing='14px';x.fillText('SLEEP',500,180);
 x.font='900 112px Cinzel';x.letterSpacing='10px';x.fillText('PARALYSIS',500,330);
 const R=rng(66);x.globalCompositeOperation='destination-out';
 for(let i=0;i<1400;i++){x.globalAlpha=.3+R()*.7;x.beginPath();x.arc(R()*1000,R()*420,R()*2.4,0,7);x.fill();}
 for(let i=0;i<26;i++){x.globalAlpha=.5+R()*.5;x.lineWidth=.6+R()*1.8;x.beginPath();const a=R()*1000,b=R()*420;x.moveTo(a,b);x.lineTo(a+(R()-.5)*120,b+(R()-.2)*260);x.stroke();}
 x.globalCompositeOperation='source-atop';x.globalAlpha=1;
 const g=x.createLinearGradient(0,0,0,420);g.addColorStop(0,'rgba(120,10,10,0)');g.addColorStop(.85,'rgba(120,10,10,.55)');g.addColorStop(1,'rgba(120,10,10,.8)');x.fillStyle=g;x.fillRect(0,0,1000,420);
 return c;}

export class Overlay{
 constructor(W,H,data){this.W=W;this.H=H;this.d=data;this.title=titleCanvas();}
 draw(x,t,fx){const {W,H}=this,{T,shots,seg,words}=this.d,s=W/1080;
  if(t>=T.black){this.eyes(x,t,s);return;}
  // ---- title: big at the opening, then pinned to the top for the rest of the reel
  const k=sm(shots[1].t0-.05,shots[1].t0+.35,t);
  const cx=W/2,cy=(H*.4)*(1-k)+(H*.085)*k,sc=s*(1.0+.04*t/2)*(1-k)+s*.5*k;
  const flick=k<1?.82+.18*fx.candle:.9;
  x.save();x.translate(cx,cy);x.scale(sc,sc);x.globalAlpha=Math.min(1,t/.12+.85)*flick;
  x.shadowColor='rgba(170,0,0,.85)';x.shadowBlur=38*sc;x.drawImage(this.title,-500,-230);x.shadowBlur=0;x.shadowColor='transparent';x.drawImage(this.title,-500,-230);x.restore();
  // ---- captions: the current line, each word lands as it is spoken; key words in blood red
  const si=seg.findIndex((g,i)=>t>=g.start-.06&&t<(seg[i+1]?Math.min(seg[i+1].start-.06,g.end+.9):g.end+.9));if(si<0)return;
  const ws=words.filter(w=>w.start>=seg[si].start-.01&&w.end<=seg[si].end+.01);
  const fs=Math.round(88*s);x.font=`700 ${fs}px Oswald`;x.textBaseline='middle';x.letterSpacing=`${2*s}px`;
  const items=ws.map(w=>({w,txt:w.word.toUpperCase(),wd:x.measureText(w.word.toUpperCase()).width}));
  const lines=[[]];let lw=0;const maxW=W*.84,sp=fs*.34;
  for(const it of items){if(lw+it.wd>maxW&&lines[lines.length-1].length){lines.push([]);lw=0;}lines[lines.length-1].push(it);lw+=it.wd+sp;}
  const lh=fs*1.12,y0=H*(t<shots[1].t0?.77:.66)-(lines.length-1)*lh/2;
  lines.forEach((ln,li)=>{const tw=ln.reduce((a,b)=>a+b.wd,0)+sp*(ln.length-1);let px=W/2-tw/2;
   for(const it of ln){const a=sm(it.w.start-.03,it.w.start+.07,t);if(a>0){const pop=1+.12*(1-sm(it.w.start,it.w.start+.14,t));const key=isKey(it.w.word);
     const jx=key?Math.sin(t*61+px)*1.6*s:0,jy=key?Math.cos(t*53+px)*1.6*s:0;
     x.save();x.translate(px+it.wd/2+jx,y0+li*lh+jy);x.scale(pop,pop);x.globalAlpha=a;x.textAlign='center';
     x.lineJoin='round';x.lineWidth=12*s;x.strokeStyle='rgba(0,0,0,.92)';x.shadowColor='rgba(0,0,0,.9)';x.shadowBlur=18*s;x.strokeText(it.txt,0,0);x.shadowBlur=0;
     if(key){x.shadowColor='rgba(255,0,0,.55)';x.shadowBlur=22*s;}
     x.fillStyle=key?'#d8141f':'#efe9dc';x.fillText(it.txt,0,0);x.restore();}
    px+=it.wd+sp;}});
 }
 // final black: two eyes open in the dark, hold, gone
 eyes(x,t,s){const {W,H}=this,T=this.d.T,o=t-T.black;const open=sm(.3,.42,o)*(1-sm(.7,.76,o));if(open<=0)return;
  for(const sd of [-1,1]){x.save();x.translate(W/2+sd*92*s,H*.43);x.rotate(sd*.18);x.scale(1,open);
   x.shadowColor='rgba(255,20,10,.95)';x.shadowBlur=60*s;const g=x.createRadialGradient(0,0,2,0,0,46*s);g.addColorStop(0,'#fff2dc');g.addColorStop(.25,'#ff3a1c');g.addColorStop(1,'rgba(120,0,0,0)');
   x.fillStyle=g;x.beginPath();x.moveTo(-50*s,0);x.quadraticCurveTo(0,-26*s,50*s,6*s);x.quadraticCurveTo(0,20*s,-50*s,0);x.fill();x.restore();}}
}
