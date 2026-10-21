// node proj.js out.json  -> per-frame screen position of the culprit site P (exterior shots), [-1,-1] inside the artery
const {chromium}=require(process.env.PW_CORE||'playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-gl=angle']});
const p=await b.newPage({viewport:{width:360,height:640}}); await p.goto(`http://localhost:${process.env.PORT||8777}/index.html?w=360&h=640`); await p.waitForFunction('window.ready===true',{timeout:180000});
const r=await p.evaluate(()=>{const o=[]; for(let f=0;f<747;f++) o.push(window.projV(f/30)); return o;}); fs.writeFileSync(process.argv[2],JSON.stringify(r)); await b.close();})();
