const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/43e84261-6c7e-57fc-924c-617953374ae4/scratchpad/spike/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,FPS=30,port=process.argv[8]||8767; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true&&window.andReady===true',{timeout:180000});
await p.evaluate(()=>window.renderAt(14.5,1));
for(let f=a;f<b2;f+=step){ const t=f/FPS; const e=1; const d=await p.evaluate(([t,e])=>window.renderAt(t,e),[t,e]); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); if(f%30===0) console.log('frame',f); }
await b.close();})();
