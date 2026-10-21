// Dumps the screen position (0-1) of the 20 CM chip anchor for every frame, for overlay.py. usage: node proj.js out.json
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const b=await chromium.launch({executablePath:process.env.CHROME||'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--use-gl=angle']});
const p=await b.newPage({viewport:{width:360,height:640}}); await p.goto(`http://localhost:${process.env.PORT||8790}/index.html?w=360&h=640`); await p.waitForFunction('window.ready===true',{timeout:120000});
const TL=JSON.parse(fs.readFileSync('timeline.json')); const out={};
for(let f=0;f<Math.round(TL.T*30);f++){ const t=f/30; if(t<TL.events.hit_reveal-0.1||t>12.0) continue; out[f]=(await p.evaluate(t=>window.projAt(t,[window.chipWorld]),t))[0]; }
fs.writeFileSync(process.argv[2],JSON.stringify(out)); await b.close();})();
