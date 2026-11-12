// node shot.js jobs.json outdir [worker nworkers] [filter-regex] -> outdir/<name>.jpg (skips existing)
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{let jobs=JSON.parse(fs.readFileSync(process.argv[2])); const out=process.argv[3]; fs.mkdirSync(out,{recursive:true});
const wk=+(process.argv[4]||0), nw=+(process.argv[5]||1), re=process.argv[6]?new RegExp(process.argv[6]):null;
jobs=jobs.filter((j,i)=>i%nw===wk&&(!re||re.test(j.name))&&!fs.existsSync(`${out}/${j.name}.jpg`));
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:1080,height:1920}}); p.on('pageerror',e=>console.log('[err]',e.message));
await p.goto('http://localhost:8790/index.html'); await p.waitForFunction('window.ready===true',{timeout:120000});
await p.evaluate(j=>window.renderLane(j.lane,j.t,64,64),jobs[0]||{lane:{club:{},cam:{pos:[0,1,4],look:[0,0,0]}},t:0});
const t0=Date.now(); let n=0;
for(const j of jobs){const d=await p.evaluate(j=>window.renderLane(j.lane,j.t,j.w,j.h),j);
 fs.writeFileSync(`${out}/${j.name}.jpg`,Buffer.from(d.split(',')[1],'base64')); n++;
 if(n%50===0) console.log(`w${wk} ${n}/${jobs.length} ${((Date.now()-t0)/n/1000).toFixed(2)}s/each`);}
console.log(`w${wk} done ${n}`); await b.close();})();
