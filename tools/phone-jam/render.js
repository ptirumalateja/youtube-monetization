// node render.js W H outdir startFrame endFrame step : interleaved frame render (run several workers with different start frames)
// output frame f renders scene time timemap.json frames[f] when that file exists, else f/30
const {chromium}=require('./node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],e=+process.argv[6],step=+process.argv[7]||1,FPS=30; const TMF=process.env.TIMEMAP||((process.env.PAGE||'index.html')==='index.html'?__dirname+'/timemap.json':''); const TM=TMF&&fs.existsSync(TMF)?JSON.parse(fs.readFileSync(TMF)).frames:null; const sceneT=f=>TM?TM[f]:f/FPS; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${process.env.PORT||8771}/${process.env.PAGE||'index.html'}?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(5));
for(let f=a;f<e;f+=step){ const fn=`${out}/f${String(f).padStart(4,'0')}.jpg`; if(fs.existsSync(fn)) continue; const d=await p.evaluate(t=>window.renderAt(t),sceneT(f)); fs.writeFileSync(fn,Buffer.from(d.split(',')[1],'base64')); if(f%30<step) console.log('frame',f); }
await b.close();})();
