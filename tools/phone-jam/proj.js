// node proj.js out.json : per-frame overlay data (counter, speed, screen positions)
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=540,H=960; const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:W,height:H}}); await p.goto(`http://localhost:${process.env.PORT||8771}/${process.env.PAGE||'index.html'}?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true');
const TMF=process.env.TIMEMAP||((process.env.PAGE||'index.html')==='index.html'?__dirname+'/timemap.json':''); const TM=TMF?JSON.parse(fs.readFileSync(TMF)).frames:Array.from({length:660},(_,f)=>f/30); const rows=[]; for(let f=0;f<TM.length;f++){ rows.push(await p.evaluate(t=>window.projAt(t),TM[f])); } fs.writeFileSync(process.argv[2],JSON.stringify(rows)); await b.close();})();
