// node proj.js port out.json  -> per-frame screen positions for overlay markers
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const port=process.argv[2],out=process.argv[3];
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:270,height:480}}); await p.goto(`http://localhost:${port}/index.html?w=270&h=480`); await p.waitForFunction('window.ready===true');
const res=[]; for(let f=0;f<720;f++) res.push(await p.evaluate(t=>window.proj(t),f/30)); fs.writeFileSync(out,JSON.stringify({tl:await p.evaluate(()=>window.TL),f:res})); await b.close();})();
