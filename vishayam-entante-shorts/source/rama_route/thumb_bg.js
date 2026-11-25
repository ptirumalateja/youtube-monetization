const { chromium } = require('playwright'); const path=require('path'); const fs=require('fs');
const cfg=JSON.parse(fs.readFileSync('rama_map5.json','utf8'));
cfg.pins=[];cfg.feet.e=999;cfg.routeOpacity=[[0,0.5]];
(async()=>{const b=await chromium.launch({args:['--ignore-gpu-blocklist']});
for(const [w,h,name,cz] of [[1080,1920,'tb_v',[79.8,28.0,4.5]],[1280,720,'tb_h',[70.6,18.0,4.6]]]){
 const c=JSON.parse(JSON.stringify(cfg)); if(cz){c.keys[c.keys.length-1].c=[cz[0],cz[1]];c.keys[c.keys.length-1].z=cz[2];c.keys[c.keys.length-1].p=0;c.keys[c.keys.length-2]=c.keys[c.keys.length-1]}
 const p=await b.newPage({viewport:{width:w,height:h}});await p.addInitScript(x=>{window.CFG=x},c);
 await p.goto('file://'+path.join(__dirname,'engine_rama.html'));await p.waitForFunction(()=>window.LOADED===true,{timeout:120000});
 const t=c.duration-0.05;await p.evaluate(t=>window.setFrame(t),t);
 await p.waitForFunction(()=>window.map.areTilesLoaded()&&window.map.loaded(),{timeout:60000,polling:100}).catch(()=>{});
 await p.evaluate(()=>new Promise(r=>setTimeout(r,1500)));await p.evaluate(t=>window.setFrame(t),t);await p.evaluate(()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r))));
 const xy=await p.evaluate(()=>{const a=window.map.project([77.6086,13.8048]);return [Math.round(a.x),Math.round(a.y)]});
 console.log(name,JSON.stringify(xy));await p.screenshot({path:`../ramathumb/${name}.png`});await p.close()}
await b.close()})();
