// node shot.js jobs.json outdir  -> renders each job {name,lane,t,w,h} to outdir/name.png
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const jobs=JSON.parse(fs.readFileSync(process.argv[2])); const out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message));
await p.goto('http://localhost:8790/index.html'); await p.waitForFunction('window.ready===true',{timeout:120000});
for(const j of jobs){const t0=Date.now(); const d=await p.evaluate(j=>window.renderLane(j.lane,j.t,j.w,j.h),j);
 fs.writeFileSync(`${out}/${j.name}.png`,Buffer.from(d.split(',')[1],'base64')); console.log(j.name,((Date.now()-t0)/1000).toFixed(1)+'s');}
await b.close();})();
