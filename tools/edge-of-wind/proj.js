// usage: node proj.js out.json port -> per-frame screen positions [voyager, sun] (0..1) for the overlay
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{ const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-gl=angle']});
const p=await b.newPage({viewport:{width:216,height:384}}); await p.goto(`http://localhost:${process.argv[3]}/index.html?w=216&h=384`); await p.waitForFunction('window.ready===true');
const o=await p.evaluate(()=>{ const r=[]; for(let f=0;f<660;f++) r.push({p:window.proj(f/30),au:window.AUat(f/30)}); return r; }); fs.writeFileSync(process.argv[2],JSON.stringify(o)); await b.close(); })();
