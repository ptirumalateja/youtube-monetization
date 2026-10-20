// Original synthesised score for "16 Sunrises a Day" (no samples). Reads events.json (node render.mjs events events.json).
// Usage: node synth.mjs events.json out.wav
import {readFileSync,writeFileSync} from 'node:fs';
const E=JSON.parse(readFileSync(process.argv[2]||'events.json','utf8')); const OUT=process.argv[3]||'mix.wav';
const SR=48000, DUR=E.DUR, N=Math.round(DUR*SR);
const bus=()=>[new Float32Array(N),new Float32Array(N)];
const B={hit:bus(),chime:bus(),bed:bus(),fx:bus(),pad:bus()};
let seed=12345; const rnd=()=>{seed=(seed*1664525+1013904223)>>>0; return seed/4294967296*2-1;};
const add=(b,i,l,r)=>{ if(i>=0&&i<N){b[0][i]+=l; b[1][i]+=r;} };
const env=(x,a,d)=>x<0?0:(x<a?x/a:Math.exp(-(x-a)/d));
// ---------- one-pole filters
function lp(x,fc){const a=1-Math.exp(-2*Math.PI*fc/SR); let y=0; const o=new Float32Array(x.length); for(let i=0;i<x.length;i++){y+=a*(x[i]-y); o[i]=y;} return o;}
function hp(x,fc){const l=lp(x,fc); const o=new Float32Array(x.length); for(let i=0;i<x.length;i++) o[i]=x[i]-l[i]; return o;}
// state-variable bandpass with time-varying centre
function bpSweep(x,fcFn,q){const o=new Float32Array(x.length); let low=0,band=0; for(let i=0;i<x.length;i++){const f=2*Math.sin(Math.PI*Math.min(fcFn(i/SR),SR/6)/SR); const high=x[i]-low-q*band; band+=f*high; low+=f*band; o[i]=band;} return o;}
// ---------- instruments
function hit(t,size,{body0=200,body1=62,sub=1,crack=1,gong=1,tail=1.6}={}){ // sized impact
  const i0=Math.round(t*SR), L=Math.round((tail+1.2)*SR); const noise=new Float32Array(L); for(let i=0;i<L;i++) noise[i]=rnd();
  const ck=hp(noise,2500); let ph=0,ps=0;
  for(let i=0;i<L;i++){ const x=i/SR; const f=body1+(body0-body1)*Math.exp(-x*9); ph+=2*Math.PI*f/SR; ps+=2*Math.PI*(body1*0.75)/SR;
    let s=Math.tanh(2.2*Math.sin(ph))*env(x,0.004,0.32*tail)*0.7*size;
    s+=ck[i]*env(x,0.0005,0.03)*0.9*crack*size;
    s+=Math.sin(ps)*env(x,0.01,0.45*tail)*0.3*sub*size;
    if(gong){ for(const [r,a,d] of [[2.76,0.16,0.9],[5.40,0.08,0.6],[8.93,0.05,0.35],[1.0,0.12,1.2]]) s+=Math.sin(2*Math.PI*body0*0.62*r*x+r)*env(x,0.002,d*tail)*a*gong*size; }
    add(B.hit,i0+i,s,s*0.98); }
}
function swell(t0,t1,size,f0=300,f1=3200,rev=false){ // filtered noise whoosh
  const i0=Math.round(t0*SR), L=Math.round((t1-t0)*SR); const x=new Float32Array(L); for(let i=0;i<L;i++) x[i]=rnd();
  const y=bpSweep(x,tt=>{const u=tt/(t1-t0); return rev?f1+(f0-f1)*u:f0*Math.pow(f1/f0,u);},0.7);
  for(let i=0;i<L;i++){ const u=i/L; const e=rev?Math.pow(u,2.2)*(1-Math.pow(u,40)):Math.sin(Math.PI*Math.pow(u,0.6)); const pan=0.5+0.4*Math.sin(u*Math.PI*1.3);
    add(B.fx,i0+i,y[i]*e*size*(1.2-pan),y[i]*e*size*(0.2+pan)); }
}
function bell(t,f,amp,dec=1.6,pan=0){ // glass FM bell
  const i0=Math.round(t*SR), L=Math.round(dec*4*SR); for(let i=0;i<L;i++){ const x=i/SR; const idx=2.4*Math.exp(-x*5); const m=Math.sin(2*Math.PI*f*3.5*x)*idx;
    const s=(Math.sin(2*Math.PI*f*x+m)*0.8+Math.sin(2*Math.PI*f*2.01*x)*0.18*Math.exp(-x*3)+Math.sin(2*Math.PI*f*4.03*x)*0.08*Math.exp(-x*6))*env(x,0.002,dec)*amp;
    add(B.chime,i0+i,s*(1-pan)*0.9,s*(1+pan)*0.9); } }
function thump(t,size){ const i0=Math.round(t*SR), L=Math.round(0.9*SR); let ph=0; for(let i=0;i<L;i++){ const x=i/SR; const f=55+150*Math.exp(-x*28); ph+=2*Math.PI*f/SR;
  const s=(Math.tanh(1.8*Math.sin(ph))*env(x,0.002,0.13)+rnd()*env(x,0.0005,0.02)*0.5)*size; add(B.hit,i0+i,s,s);} }
function tone(t0,t1,fFn,amp,ampFn,bus=B.pad,detune=[0,7,-5]){ const i0=Math.round(t0*SR), L=Math.round((t1-t0)*SR); const ph=detune.map(()=>(rnd()+1)*3.14);
  for(let i=0;i<L;i++){ const tt=i/SR, u=i/L; const f=fFn(tt,u); let s=0; detune.forEach((c,k)=>{ ph[k]+=2*Math.PI*f*Math.pow(2,c/1200)/SR; s+=Math.sin(ph[k])+0.3*Math.sin(2*ph[k])+0.12*Math.sin(3*ph[k]); });
    const v=s/detune.length*amp*ampFn(u,tt); add(bus,i0+i,v*(1+0.3*Math.sin(tt*1.7)),v*(1-0.3*Math.sin(tt*1.7))); } }
// ---------- cue sheet (times from the scene)
const SRS=E.SUNRISES; const PENTA=[0,2,4,7,9]; const noteF=k=>220*Math.pow(2,(12*Math.floor(k/5)+PENTA[k%5])/12);
SRS.forEach((t,k)=>{ bell(t,noteF(k),k===15?0.42:0.30,k===15?2.4:1.5,((k%2)?0.35:-0.35)); if(k>0) hit(t,0.10+0.012*k,{body0:320,body1:140,sub:0,gong:0,tail:0.5}); });
// frame 0: dawn hit (loop lands here) + the first chime
hit(0,0.9,{body0:220,body1:88,tail:1.4});
// bed: cabin air + 110 Hz drone with slow pulse (ducked under the cannon, held breath and closure)
{ const L=N; const x=new Float32Array(L); for(let i=0;i<L;i++) x[i]=rnd(); const air=lp(hp(x,350),2400);
  for(let i=0;i<L;i++){ const tt=i/SR; const s=air[i]*0.05+(Math.sin(2*Math.PI*110*tt)*0.5+Math.sin(2*Math.PI*165*tt)*0.25+Math.sin(2*Math.PI*220.4*tt)*0.15)*0.05*(0.75+0.25*Math.sin(2*Math.PI*0.5*tt));
    add(B.bed,i,s,s*0.97); } }
// snap out to orbit
swell(1.75,2.95,0.55,250,4200); hit(2.25,0.45,{body0:260,body1:95,gong:0.5,tail:0.9});
// time-lapse riser: rising tone + accelerating shimmer, tape-stop at 11.35
tone(3.2,11.5,(tt)=>110*Math.pow(2,(tt/8.15)*1.0),0.05,(u,tt)=>Math.min(1,u*1.4)*(tt>8.0?Math.max(0,1-(tt-8.0)/0.25):1));
tone(11.0,11.6,(tt)=>220*Math.pow(2,-tt*2.6),0.07,(u)=>Math.sin(Math.PI*u));
swell(10.6,11.5,0.18,800,6000);
thump(11.65,0.55); // "IT ISN'T FLOATING."
// cannon
E.ARCS.forEach((a,i)=>{ thump(a.t0,0.45+0.15*i); swell(a.t0,a.t1+0.05,0.12+0.06*i,600,2400-300*i,true);
  if(i<3) { thump(a.t1,0.28+0.05*i); hit(a.t1,0.12,{body0:180,body1:70,sub:0.4,gong:0,tail:0.4}); } });
// arc 4: around the world, rising tone into the closure
tone(15.7,17.42,(tt,u)=>146.8*Math.pow(2,u*1.0),0.17,(u)=>Math.pow(u,1.4));
swell(16.4,17.4,0.42,300,5200,true);
hit(E.closure,1.3,{body0:240,body1:80,tail:2.4,gong:1.2});
tone(17.4,20.2,()=>220,0.07,(u)=>Math.min(1,u*6)*Math.pow(1-u,1.5),B.pad,[0,5,-7,12]);
tone(17.4,20.2,()=>329.6,0.045,(u)=>Math.min(1,u*6)*Math.pow(1-u,1.5),B.pad,[0,-4,9]);
bell(18.3,659.3,0.14,1.4,0.2);
// plunge home
swell(18.95,20.6,0.5,5000,300,false); tone(19.0,20.6,(tt,u)=>330*Math.pow(2,-u*1.5),0.06,(u)=>Math.sin(Math.PI*u));
hit(20.6,0.35,{body0:190,body1:92,gong:0.4,tail:1.0});
// night: faint dawn riser into the loop
tone(21.3,22.5,(tt,u)=>110*Math.pow(2,u*0.5),0.07,(u)=>Math.pow(u,2.5)*(u>0.985?0:1));
swell(21.6,22.48,0.22,400,5000,true);
// ---------- mix
const gain=(t)=>{ // held breath / ducks
  let g=1; const hb=(a,b,c,d,depth)=>{ g*=1-depth*Math.min(Math.max((t-a)/(b-a),0),1)*(1-Math.min(Math.max((t-c)/(d-c),0),1)); };
  hb(15.12,15.25,15.62,15.7,0.97); hb(22.40,22.44,22.49,22.5,0.9); return g; };
function reverb(b,mix,decay){ // small Schroeder
  const combs=[1557,1617,1491,1422].map(d=>Math.round(d*SR/44100)), aps=[225,556].map(d=>Math.round(d*SR/44100));
  for(const ch of [0,1]){ const x=b[ch]; const y=new Float32Array(N);
    combs.forEach((d,k)=>{ const buf=new Float32Array(d+ch*23); let p=0; for(let i=0;i<N;i++){ const o=buf[p]; buf[p]=x[i]+o*decay; p=(p+1)%buf.length; y[i]+=o*0.25; } });
    let z=y; for(const d of aps){ const buf=new Float32Array(d); let p=0; const o=new Float32Array(N); for(let i=0;i<N;i++){ const bo=buf[p]; const v=z[i]+bo*0.5; buf[p]=v; o[i]=bo-v*0.5; p=(p+1)%d; } z=o; }
    for(let i=0;i<N;i++) x[i]+=z[i]*mix; } }
reverb(B.hit,0.35,0.82); reverb(B.chime,0.45,0.86); reverb(B.pad,0.3,0.8);
// bass management: everything but the hit bus is high-passed at 90 Hz
for(const k of ['chime','bed','fx','pad']) for(const ch of [0,1]) B[k][ch]=hp(hp(B[k][ch],90),90);
const L=new Float32Array(N), R=new Float32Array(N); const lv={hit:1.0,chime:0.9,bed:0.8,fx:0.8,pad:0.9};
// side-chain: duck non-hit buses under the hit bus envelope
let envH=0; for(let i=0;i<N;i++){ const h=Math.abs(B.hit[0][i]); envH=Math.max(h,envH*0.9997); const duck=1/(1+envH*1.2); const g=gain(i/SR);
  let l=B.hit[0][i]*lv.hit, r=B.hit[1][i]*lv.hit; for(const k of ['chime','bed','fx','pad']){ l+=B[k][0][i]*lv[k]*duck; r+=B[k][1][i]*lv[k]*duck; }
  L[i]=Math.tanh(l*g*1.1); R[i]=Math.tanh(r*g*1.1); }
let pk=0; for(let i=0;i<N;i++) pk=Math.max(pk,Math.abs(L[i]),Math.abs(R[i])); const nrm=0.89/pk;
const buf=Buffer.alloc(44+N*2*4); buf.write('RIFF',0); buf.writeUInt32LE(36+N*8,4); buf.write('WAVEfmt ',8); buf.writeUInt32LE(16,16); buf.writeUInt16LE(3,20); buf.writeUInt16LE(2,22); buf.writeUInt32LE(SR,24); buf.writeUInt32LE(SR*8,28); buf.writeUInt16LE(8,32); buf.writeUInt16LE(32,34); buf.write('data',36); buf.writeUInt32LE(N*8,40);
for(let i=0;i<N;i++){ buf.writeFloatLE(L[i]*nrm,44+i*8); buf.writeFloatLE(R[i]*nrm,48+i*8); } writeFileSync(OUT,buf); console.log('wrote',OUT,'peak norm',nrm.toFixed(3));
