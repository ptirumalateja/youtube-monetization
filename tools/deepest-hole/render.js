// usage: node render.js W H outDir startFrame endFrame step   (interleave workers with step/offset)
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${process.env.PORT||8791}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
for(let f=a;f<b2;f+=step){ const d=await p.evaluate(t=>window.renderAt(t,3),f/FPS); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); if(f%30===0) console.log('frame',f); }
await b.close();})();
