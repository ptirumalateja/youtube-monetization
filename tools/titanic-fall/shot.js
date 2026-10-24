// node shot.js <w> <h> <outdir> <id:t> ...   renders look-dev stills (G1)
const {chromium}=require('playwright'); const fs=require('fs');
(async()=>{const [W,H,out]=[+process.argv[2],+process.argv[3],process.argv[4]]; const jobs=process.argv.slice(5).map(s=>s.split(':').map(Number)); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,400)));
await p.goto(`http://localhost:${process.env.PORT||8771}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
for(const [id,t,sub] of jobs){const t0=Date.now(); const d=await p.evaluate(([id,t,sub])=>window.renderLook(id,t,sub),[id,t,sub||1]); fs.writeFileSync(`${out}/look${id}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log('look',id,((Date.now()-t0)/1000).toFixed(1)+'s');}
await b.close();})();
