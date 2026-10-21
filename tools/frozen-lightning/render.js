// node render.js W H outdir firstFrame endFrame step port -> frames f####.jpg + proj_<first>.json (screen anchors for the overlay)
const {chromium}=require('playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],e=+process.argv[6],step=+process.argv[7]||1,port=process.argv[8]||8777,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',x=>console.log('[err]',x.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(8.0)); const proj={};
for(let f=a;f<e;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)&&!process.env.FORCE){ proj[f]=await p.evaluate(t=>window.projAt(t),f/FPS); continue; } const d=await p.evaluate(t=>window.renderAt(t),f/FPS); proj[f]=d.proj; fs.writeFileSync(fn,Buffer.from(d.img.split(',')[1],'base64')); if(f%30===a%30) console.log('frame',f); }
fs.writeFileSync(`${out}/proj_${a}.json`,JSON.stringify(proj)); await b.close();})();
