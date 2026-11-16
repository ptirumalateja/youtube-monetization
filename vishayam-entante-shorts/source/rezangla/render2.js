const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1400,height:2800}});
await p.goto('file://'+path.join(__dirname,'rl2.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await (await p.$('#v')).screenshot({path:process.argv[2]+'/v2_cover.png'});
await (await p.$('#h')).screenshot({path:process.argv[2]+'/v2_thumb.png'});await b.close();})();
