// node shoot.js W H outdir shot...  (serve this folder on :8771 first)
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const [W,H,out,...shots]=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:+W,height:+H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:8771/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:60000});
for(const s of shots){const t0=Date.now(); const d=await p.evaluate(n=>window.renderShot(n),s); fs.writeFileSync(`${out}/${s}.png`,Buffer.from(d.split(',')[1],'base64')); console.log(s,((Date.now()-t0)/1000).toFixed(1)+'s');}
await b.close();})();
