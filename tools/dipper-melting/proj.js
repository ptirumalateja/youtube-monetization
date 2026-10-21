// dump overlay anchors for every frame: node proj.js out.json
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-gl=angle']});
const p=await b.newPage({viewport:{width:270,height:480}}); await p.goto('http://localhost:8771/index.html?w=270&h=480'); await p.waitForFunction('window.ready===true');
const r=await p.evaluate(()=>{const o=[]; for(let f=0;f<600;f++) o.push(window.proj(f/30)); return o;}); fs.writeFileSync(process.argv[2],JSON.stringify(r)); await b.close();})();
