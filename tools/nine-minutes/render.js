// node render.js W H outdir fromFrame toFrame step nsub : frames f####.jpg (interleave workers with step)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const [W,H,out,a,b2,step,nsub]=process.argv.slice(2); const FPS=30, port=process.env.PORT||8771; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:+W,height:+H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(9,1));
for(let f=+a;f<+b2;f+=+step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const t=f/FPS;
  const d=await p.evaluate(([t,n])=>window.renderAt(t,n),[t,+nsub||2]); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%30<+step) console.log('frame',f); }
await b.close();})();
