const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/8627dfa8-7a31-5632-90e9-3b8c5054ed76/scratchpad/bh/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2],H=+process.argv[3],out=process.argv[4],a=+process.argv[5],b2=+process.argv[6],step=+process.argv[7]||1,nsub=+process.argv[8]||2,port=process.env.PORT||8767,FPS=30; fs.mkdirSync(out,{recursive:true});
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:240000});
for(let f=a;f<b2;f+=step){ const t=f/FPS; const d=await p.evaluate(([t,n])=>window.renderAt(t,1,n,1/60),[t,nsub]); fs.writeFileSync(`${out}/f${String(f).padStart(4,'0')}.jpg`,Buffer.from(d.split(',')[1],'base64')); if(f%15===0) console.log('frame',f); }
await b.close();})();
