const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox']});
const p=await b.newPage(); await p.goto('http://localhost:8778/index.html'); await p.waitForFunction('window.ready===true');
const ev=await p.evaluate(()=>({rain:RAIN.map(r=>r.t),drops:DROPS.map(d=>[d.t,d.b,d.fine?1:0])})); fs.writeFileSync('events.json',JSON.stringify(ev)); await b.close();})();
