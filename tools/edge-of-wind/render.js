// usage: node render.js W H outdir first last step port   -> frames f0000.jpg.. (30 fps, interleave workers with step)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{ const [W,H,out,a,z,step,port]=process.argv.slice(2).map((v,i)=>i==2?v:+v); fs.mkdirSync(out,{recursive:true}); const FPS=30;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000}); await p.evaluate(()=>window.renderAt(5,1));
for(let f=a;f<z;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const d=await p.evaluate(t=>window.renderAt(t,2),f/FPS); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%60<step) console.log('frame',f); }
await b.close(); })();
