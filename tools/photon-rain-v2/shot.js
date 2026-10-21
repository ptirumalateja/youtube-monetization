const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const out=process.argv[2],ts=process.argv.slice(3).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto('http://localhost:8778/index.html'); await p.waitForFunction('window.ready===true',{timeout:60000});
for(const t of ts){const t1=Date.now(); const d=await p.evaluate(t=>window.renderAt(t),t); fs.writeFileSync(`${out}/t${t.toFixed(2)}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,(Date.now()-t1)+'ms');} await b.close();})();
