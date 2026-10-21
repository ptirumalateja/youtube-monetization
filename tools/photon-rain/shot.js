const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],ts=process.argv.slice(5).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
const t0=Date.now(); await p.goto(`http://localhost:8777/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:300000}); console.log('load',(Date.now()-t0)/1000);
for(const t of ts){const t1=Date.now(); const r=await p.evaluate(t=>window.renderAt(t,3),t); fs.writeFileSync(`${out}/t${t.toFixed(2)}.jpg`,Buffer.from(r.img.split(',')[1],'base64')); console.log(t,((Date.now()-t1)/1000).toFixed(1)+'s',JSON.stringify({cPh:r.info.cPh,cFF:r.info.cFF,sPh:r.info.sPh.toFixed(3),sFF:r.info.sFF.toFixed(4)}));} await b.close();})();
