const {chromium}=require('playwright');const path=require('path');
(async()=>{const b=await chromium.launch();const p=await b.newPage();await p.goto('file://'+path.resolve(__dirname,'index.html')+'?reel='+(process.env.REEL||'reel.js'));await p.waitForFunction('window.ready===true');
const r=await p.evaluate(()=>{let t=0;return{dur:window.DUR,scenes:window.REEL.scenes.map(s=>{const o={type:s.type,t0:t,dur:s.dur,instant:!!s.instant,chip:s.chip||''};t+=s.dur;return o})}});
console.log(JSON.stringify(r));await b.close();})();
