// node shot.js W H outDir t1 t2 ...   test stills
const {chromium}=require(process.env.PW_CORE||'playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],ts=process.argv.slice(5).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text().slice(0,300))); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${process.env.PORT||8777}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
for(const t of ts){const t0=Date.now(); const d=await p.evaluate(([t])=>window.renderAt(t,1),[t]); fs.writeFileSync(`${out}/t${t.toFixed(2)}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,((Date.now()-t0)/1000).toFixed(1)+'s');} await b.close();})();
