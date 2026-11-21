// usage: node shot.js <outdir> <t1,t2,...|all> [fps]
const {chromium}=require('playwright');const fs=require('fs');const path=require('path');
(async()=>{const out=process.argv[2],which=process.argv[3]||'0',FPS=+(process.argv[4]||30);fs.mkdirSync(out,{recursive:true});
const EXT=process.env.OVERLAY?'png':'jpg';const b=await chromium.launch();const p=await b.newPage({viewport:{width:1080,height:1920}});
p.on('pageerror',e=>console.log('[err]',e.message));p.on('console',m=>console.log('[log]',m.text()));
await p.goto('file://'+path.resolve(__dirname,'index.html')+'?reel='+(process.env.REEL||'reel.js')+(process.env.OVERLAY?'&overlay=1':''));await p.waitForFunction('window.ready===true');
const dur=await p.evaluate(()=>window.DUR);console.log('DUR',dur);
const ts=which==='all'?Array.from({length:Math.ceil(dur*FPS)},(_,i)=>i/FPS):which.split(',').map(Number);
for(let i=0;i<ts.length;i++){const d=await p.evaluate(t=>window.renderAt(t),ts[i]);
  fs.writeFileSync(`${out}/${which==='all'?'f'+String(i).padStart(4,'0'):'t'+ts[i].toFixed(2)}.${EXT}`,Buffer.from(d.split(',')[1],'base64'));
  if(which==='all'&&i%60===0)console.log('frame',i);}
await b.close();})();
