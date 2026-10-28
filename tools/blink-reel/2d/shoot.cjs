// node shoot.cjs OUTDIR -> eye.png, dusk.png, mirror.png (1080x1920)
const {chromium}=require('playwright'); const fs=require('fs'), path=require('path');
(async()=>{ const out=process.argv[2]; fs.mkdirSync(out,{recursive:true}); const b=await chromium.launch(); const p=await b.newPage({viewport:{width:1080,height:1920}});
  await p.goto('file://'+path.join(__dirname,'frames.html')); await p.waitForFunction('window.ready');
  for(const n of ['eye','dusk','mirror']){ const d=await p.evaluate(n=>window.draw(n),n); fs.writeFileSync(path.join(out,n+'.png'),Buffer.from(d.split(',')[1],'base64')); console.log(n); }
  await b.close(); })();
