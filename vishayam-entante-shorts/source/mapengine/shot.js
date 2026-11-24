const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();
const p=await b.newPage({viewport:{width:540,height:960}});
p.on('console',m=>console.log('console:',m.text().slice(0,200)));
p.on('pageerror',e=>console.log('PAGEERR',e.message.slice(0,300)));p.on('requestfailed',r=>console.log('FAIL',r.url().slice(0,100),r.failure()&&r.failure().errorText));
await p.goto('file://'+path.join(__dirname,'test.html'));
await p.waitForFunction(()=>window.READY===true,{timeout:60000}).catch(e=>console.log('timeout'));
await p.screenshot({path:path.join(__dirname,'test.png')});await b.close();})();
