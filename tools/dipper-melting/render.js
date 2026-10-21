// frames: node render.js W H outdir firstFrame endFrame step   (run several workers with different first frames)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:8771/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(5));
for(let f=a;f<b2;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const d=await p.evaluate(t=>window.renderAt(t),f/FPS); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%30<step) console.log('frame',f); }
await b.close();})();
