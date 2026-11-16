const { chromium } = require('playwright'); const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage({viewport:{width:1100,height:1100}});
await p.goto('file://'+path.join(__dirname,'card.html'));await p.evaluate(()=>document.fonts.ready);await p.waitForTimeout(800);
for (const id of ['a','b']) { const el=await p.$('#'+id); const bb=await el.boundingBox();
 await p.screenshot({path:path.join(__dirname,`card_${id}.png`),omitBackground:true,clip:{x:bb.x,y:bb.y,width:bb.width,height:bb.height+70}}); }
await b.close();})();
