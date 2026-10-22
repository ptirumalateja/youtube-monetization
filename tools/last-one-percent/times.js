// node times.js port out.json -> per-frame overlay data (head position, battery), foot contacts, beats
const {chromium}=require('playwright-core');const fs=require('fs');
(async()=>{const [port,out]=process.argv.slice(2);
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:1080,height:1920}});
await p.goto(`http://localhost:${port}/index.html?w=1080&h=1920`);await p.waitForFunction('window.ready===true',{timeout:120000});
const r=await p.evaluate(()=>{const NF=Math.round(window.DUR*30);const proj=[];for(let f=0;f<NF;f++)proj.push(window.proj(f/30));return {...window.timing(),proj,steps:window.steps(),leaps:window.leaps()};});
fs.writeFileSync(out,JSON.stringify(r));console.log('frames',r.proj.length,'steps',r.steps.length);await b.close();})();
