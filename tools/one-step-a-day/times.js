// node times.js port out.json -> placement times + per-frame day counter for the overlay and the mix
const {chromium}=require('playwright-core');const fs=require('fs');
(async()=>{const [port,out]=process.argv.slice(2);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:108,height:192}});await p.goto(`http://localhost:${port}/index.html?w=108&h=192`);await p.waitForFunction('window.ready===true');
const r=await p.evaluate(()=>{const FPS=30,NF=Math.round(window.DUR*FPS),days=[];for(let f=0;f<NF;f++)days.push(window.placed(f/FPS));return {place:window.placeTimes(),days,dur:window.DUR};});
fs.writeFileSync(out,JSON.stringify(r));await b.close();})();
