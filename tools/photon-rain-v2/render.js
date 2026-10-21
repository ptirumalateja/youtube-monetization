const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const out=process.argv[2]; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto('http://localhost:8778/index.html'); await p.waitForFunction('window.ready===true');
for(let f=0;f<960;f++){ const d=await p.evaluate(t=>window.renderAt(t),f/30); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); }
await b.close(); console.log('done');})();
