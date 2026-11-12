const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const jobs=JSON.parse(fs.readFileSync(process.argv[2])); const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); let t0=Date.now();
await p.goto('http://localhost:8790/index.html'+(process.argv[3]||'')); await p.waitForFunction('window.ready===true'); console.log('load',(Date.now()-t0)/1000);
for(const n of (process.argv[4]||'f0360_full,f0360_full,f0360_full').split(',')){const j=jobs.find(x=>x.name===n); t0=Date.now(); await p.evaluate(j=>window.renderLane(j.lane,j.t,j.w,j.h),j); console.log(n,(Date.now()-t0)/1000);}
await b.close();})();
