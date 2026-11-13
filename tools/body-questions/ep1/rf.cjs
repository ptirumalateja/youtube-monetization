// node rf.cjs jobs.json outdir   jobs: [{name, params}]
const {chromium}=require('playwright');const fs=require('fs');
(async()=>{const [,,jobsf,out]=process.argv;const jobs=JSON.parse(fs.readFileSync(jobsf));fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({args:['--use-gl=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:1080,height:1920}});p.on('pageerror',e=>console.log('ERR',e.message));
await p.goto('file://'+__dirname+'/shots.html');await p.waitForFunction('window.READY');
for(const j of jobs){const f=out+'/'+j.name+'.jpg';if(fs.existsSync(f))continue;const t0=Date.now();
 const d=await p.evaluate(P=>window.render(P),j.params);fs.writeFileSync(f,Buffer.from(d.split(',')[1],'base64'));
 if(j.log)console.log(j.name,Date.now()-t0,'ms');}
await b.close();})();
