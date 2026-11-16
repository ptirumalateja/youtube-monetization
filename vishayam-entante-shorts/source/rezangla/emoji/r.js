const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:400,height:300}});
await p.goto('file://'+path.join(__dirname,'e.html'));await p.waitForTimeout(500);
await (await p.$('#e')).screenshot({path:path.join(__dirname,'flag_emoji.png'),omitBackground:true});await b.close();})();
