// usage: node shot.js W H outDir t1 t2 ...   (needs `python3 -m http.server 8790` in this directory)
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],ts=process.argv.slice(5).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:${process.env.PORT||8790}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:120000});
for(const t of ts){const t0=Date.now(); const d=await p.evaluate(t=>window.renderAt(t,2),t); fs.writeFileSync(`${out}/t${String(t).replace('.','_')}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,((Date.now()-t0)/1000).toFixed(1)+'s');} await b.close();})();
