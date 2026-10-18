// usage: node shot.js <playwright-core dir> <w> <h> <outdir> <t1> <t2> ...   (server: python3 -m http.server 8766 in this dir)
const {chromium}=require(process.argv[2]); const fs=require('fs');
(async()=>{const W=+process.argv[3],H=+process.argv[4],out=process.argv[5],ts=process.argv.slice(6).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:8766/${process.env.PAGE||'opening.html'}?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:120000});
for(const t of ts){const t0=Date.now(); const d=await p.evaluate(([t])=>window.renderAt(t),[t]); fs.writeFileSync(`${out}/t${String(t).replace('.','_')}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,((Date.now()-t0)/1000).toFixed(1)+'s');} await b.close();})();
