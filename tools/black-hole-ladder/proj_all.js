const {chromium}=require('/tmp/claude-0/-home-user-youtube-monetization/8627dfa8-7a31-5632-90e9-3b8c5054ed76/scratchpad/bh/node_modules/playwright-core'); const fs=require('fs');
(async()=>{const W=+process.argv[2]||360,H=+process.argv[3]||640,out=process.argv[4],n=+process.argv[5]||846,port=process.env.PORT||8767;
const b=await chromium.launch({executablePath:'/opt/pw-browsers/chromium-1194/chrome-linux/chrome',args:['--no-sandbox','--use-angle=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist','--use-gl=angle']});
const p=await b.newPage({viewport:{width:W,height:H}}); p.on('pageerror',e=>console.log('[err]',e.message.slice(0,300)));
await p.goto(`http://localhost:${port}/index.html?w=${W}&h=${H}`); await p.waitForFunction('window.ready===true',{timeout:240000});
const res=await p.evaluate((n)=>{ const a=[]; for(let f=0;f<n;f++) a.push(window.projAll(f/30)); return a; },n);
fs.writeFileSync(out,JSON.stringify(res)); console.log('frames',res.length); await b.close();})();
