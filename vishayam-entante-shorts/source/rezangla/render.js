const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1400,height:2800}});
await p.goto('file://'+path.join(__dirname,'rl.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
await (await p.$('#v')).screenshot({path:process.argv[2]+'/rezangla_cover_1080x1920.png'});
await (await p.$('#h')).screenshot({path:process.argv[2]+'/rezangla_thumbnail_1280x720.png'});await b.close();})();
