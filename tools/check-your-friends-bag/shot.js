// node shot.js W H outdir port t1 t2 ...  -> stills (one sample) for checking the shot plan
const fs=require('fs');const {open}=require('./browser.js');
(async()=>{const [W,H,out,port,...ts]=process.argv.slice(2);fs.mkdirSync(out,{recursive:true});const {b,p}=await open(W,H,port);
for(const t of ts){const t0=Date.now();const d=await p.evaluate(t=>window.renderAt(+t,1),t);fs.writeFileSync(`${out}/s_${(+t).toFixed(2)}.jpg`,Buffer.from(d.split(',')[1],'base64'));console.log(t,Date.now()-t0,'ms');}
await b.close();})();
