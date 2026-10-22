// node times.js port out.json -> strike times + per-frame year and metres for the overlay and the mix
const {chromium}=require('playwright-core');const fs=require('fs');
(async()=>{const [port,out]=process.argv.slice(2);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader']});
const p=await b.newPage({viewport:{width:108,height:192}});await p.goto(`http://localhost:${port}/index.html?w=108&h=192`);await p.waitForFunction('window.ready===true');
const r=await p.evaluate(()=>{const FPS=30,NF=Math.round(window.DUR*FPS),year=[],m=[];for(let f=0;f<NF;f++){const c=window.counters(f/FPS);year.push(c.year);m.push(c.m);}
  return {strikes:window.strikeTimes(),year,m,dur:window.DUR,drop:window.DROP};});
fs.writeFileSync(out,JSON.stringify(r));await b.close();})();
