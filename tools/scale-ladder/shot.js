const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/43e84261-6c7e-57fc-924c-617953374ae4/scratchpad/spike/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],ts=process.argv.slice(5).map(Number); fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('console',m=>console.log('[page]',m.text())); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:8766/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true&&window.earthReady===true',{timeout:120000});
for(const t of ts){const t0=Date.now(); const e=t<0.5?0.12+0.88*(t/0.5):1; const d=await p.evaluate(([t,e])=>window.renderAt(t,e),[t,e]); fs.writeFileSync(`${out}/t${t}_${Date.now()%100000}.jpg`,Buffer.from(d.split(',')[1],'base64')); console.log(t,((Date.now()-t0)/1000).toFixed(1)+'s');} await b.close();})();
