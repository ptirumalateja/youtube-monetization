// node proj.js out.json : per-frame overlay data (counter, speed, screen positions)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=540,H=960; const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:W,height:H}}); await p.goto(`http://localhost:${process.env.PORT||8771}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true');
const rows=[]; for(let f=0;f<660;f++){ rows.push(await p.evaluate(t=>window.projAt(t),f/30)); } fs.writeFileSync(process.argv[2],JSON.stringify(rows)); await b.close();})();
