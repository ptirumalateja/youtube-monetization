// usage: node render.js <playwright-core dir> <w> <h> <outdir> <frameStart> <frameEnd> [fps=30]   (serves city.html on :8767)
const {chromium}=require(process.argv[2]); const fs=require('fs');
(async()=>{const W=+process.argv[3],H=+process.argv[4],out=process.argv[5],a=+process.argv[6],b2=+process.argv[7],FPS=+process.argv[8]||30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300))); p.on('console',m=>{if(m.type()==='error')console.log('[console]',m.text().slice(0,200))});
await p.goto(`http://localhost:${process.env.PORT||8768}/${process.env.PAGE||'city.html'}?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:120000});
const st=[]; for(let f=a;f<b2;f++){const t=f/FPS; const d=await p.evaluate(([t])=>window.renderAt(t),[t]); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); st.push(await p.evaluate(([t])=>window.stateAt(t),[t]))}
fs.writeFileSync(`${out}/state_${a}_${b2}.json`,JSON.stringify(st)); await b.close();})();
