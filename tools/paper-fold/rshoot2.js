// node rshoot.js W H out.json  : renders layers listed in a job json [{file,name,p}] ; saves jpg + marks
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const [W,H,jobf,port]=process.argv.slice(2); const jobs=JSON.parse(fs.readFileSync(jobf));
const b=await chromium.launch({args:['--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist']});
const p=await b.newPage({viewport:{width:+W,height:+H}}); p.on('console',m=>{const t=m.text(); if(!/GPU stall|swiftshader/i.test(t))console.log('[page]',t.slice(0,300))}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:${port||8771}/reel2.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:60000});
const out=[]; const t00=Date.now();
for(const j of jobs){const t0=Date.now(); const r=await p.evaluate(([n,pp])=>window.renderLayer(n,pp),[j.name,j.p]); fs.writeFileSync(j.file,Buffer.from(r.img.split(',')[1],'base64')); out.push({file:j.file,marks:r.marks,key:j.key}); console.log(j.file.split('/').pop(),((Date.now()-t0)/1000).toFixed(1)+'s');}
fs.writeFileSync(jobf.replace('.json','.out.json'),JSON.stringify(out)); await b.close();})();
