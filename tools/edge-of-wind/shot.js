// usage: node shot.js W H outdir port t1 t2 ...   -> test stills
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{ const [W,H,out,port,...ts]=process.argv.slice(2); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:+W,height:+H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400))); p.on('console',m=>{ if(m.type()==='error'||m.type()==='warning') console.log('[con]',m.text().slice(0,400)); });
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
for(const t of ts){ const t0=Date.now(); const d=await p.evaluate(t=>window.renderAt(t,1),+t); fs.writeFileSync(`${out}/s_${(+t).toFixed(2)}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log('t',t,Date.now()-t0,'ms'); }
await b.close(); })();
