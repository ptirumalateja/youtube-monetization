// Dumps the screen position (0-1) of every chip anchor for every frame it is shown, for overlay.py. usage: node proj.js out.json
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-gl=angle']});
const p=await b.newPage({viewport:{width:360,height:640}}); await p.goto(`http://localhost:${process.env.PORT||8791}/index.html?w=360&h=640`); await p.waitForFunction('window.ready===true',{timeout:120000});
const TL=JSON.parse(fs.readFileSync('timeline.json')); const out={};
for(let f=0;f<Math.round(TL.T*30);f++){ const t=f/30; const pts=TL.chips.map(c=>c.at); out[f]=await p.evaluate(([t,pts])=>window.projAt(t,pts),[t,pts]); }
fs.writeFileSync(process.argv[2],JSON.stringify(out)); await b.close();})();
