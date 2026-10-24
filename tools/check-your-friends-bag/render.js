// node render.js W H outdir port worker nworkers  -> frames f0000.jpg.. (interleaved across workers), motion-blurred
const fs=require('fs');const {open}=require('./browser.js');
(async()=>{const [W,H,out,port,wi,nw]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});const FPS=30;const {b,p}=await open(W,H,port);
const DUR=await p.evaluate(()=>window.DUR);const NF=Math.round(DUR*FPS);
for(let f=+wi;f<NF;f+=+nw){const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`;if(fs.existsSync(fn))continue;const t=f/FPS;
  // more sub-frames where the camera or the figures move fast (drop, whip, time-lapse, pull-back)
  const n=(t>3.0&&t<3.7)||(t>5.95&&t<6.45)||(t>9.7&&t<10.2)||(t>13.6&&t<17.6)?5:3;
  const d=await p.evaluate(([t,n])=>window.renderAt(t,n),[t,n]);fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64'));if(f%40<+nw)console.log('frame',f);}
await b.close();})();
