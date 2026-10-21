const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:8777/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:300000});
for(let f=a;f<b2;f+=step){ const t=f/FPS; const r=await p.evaluate(t=>window.renderAt(t,3),t); const n=String(f).padStart(4,'0');
  fs.writeFileSync(`${out}/f${n}.jpg`,Buffer.from(r.img.split(',')[1],'base64')); fs.writeFileSync(`${out}/f${n}.json`,JSON.stringify(r.info)); if(f%40<step) console.log('frame',f); }
await b.close();})();
