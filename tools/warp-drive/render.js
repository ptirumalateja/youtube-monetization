// node render.js W H outdir port fStart fEnd step  -> frames f0000.jpg (interleave workers with step)
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const [W,H]=[+process.argv[2],+process.argv[3]],out=process.argv[4],port=process.argv[5],a=+process.argv[6],e=+process.argv[7],step=+process.argv[8]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',x=>console.log('[err]',x.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
for(let f=a;f<e;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const d=await p.evaluate(t=>window.renderAt(t),f/FPS); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%30<step) console.log('frame',f); }
await b.close();})();
