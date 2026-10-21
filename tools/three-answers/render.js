// node render.js W H outdir firstFrame endFrame step  (worker k renders frames k, k+step, ...; 30 fps)
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],e=+process.argv[6],step=+process.argv[7]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',x=>console.log('[err]',x.message.slice(0,300)));
await p.goto(`http://localhost:8777/index.html?w=${W}&h=${H}&sub=${process.env.SUB||3}`); await p.waitForFunction('window.ready===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(5));
for(let f=a;f<e;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const d=await p.evaluate(t=>window.renderAt(t),f/FPS); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%60<step) console.log('frame',f); }
await b.close();})();
