const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const [,,cfgPath,outDir,fpsArg,startArg,endArg,w,h]=process.argv;
const cfg=JSON.parse(fs.readFileSync(cfgPath,'utf8')); const FPS=+fpsArg||24;
(async()=>{fs.mkdirSync(outDir,{recursive:true});
const b=await chromium.launch({args:['--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:+w||1080,height:+h||1920}});
p.on('pageerror',e=>console.log('PAGEERR',e.message));
await p.addInitScript(c=>{window.CFG=c},cfg);
await p.goto('file://'+path.join(__dirname,'engine.html'));
await p.waitForFunction(()=>window.LOADED===true,{timeout:120000});
const t0=+startArg||0, t1=endArg?+endArg:cfg.duration; const N=Math.round((t1-t0)*FPS);
for(let i=0;i<N;i++){const t=t0+i/FPS;
 await p.evaluate(t=>window.setFrame(t),t);
 await p.waitForFunction(()=>window.map.areTilesLoaded()&&window.map.loaded(),{timeout:20000,polling:50}).catch(()=>{});
 await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 await p.screenshot({path:path.join(outDir,`f${String(i).padStart(5,'0')}.jpg`),type:'jpeg',quality:92});
 if(i%24==0)console.log('frame',i,'/',N,'t=',t.toFixed(2));}
await b.close();})();
